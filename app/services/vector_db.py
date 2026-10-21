import os
import uuid
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from sklearn.feature_extraction.text import HashingVectorizer
from app.config import settings
from app.data.default_faq import DEA_TRANS_FAQ_DOCUMENTS
from app.services.chunker import text_chunker, TextChunk

logger = logging.getLogger(__name__)


class FastLocalEmbeddingFunction(EmbeddingFunction):
    """
    Embedding function lokal berbasis L2-normalized HashingVectorizer.
    Mengubah teks menjadi representasi vektor numerik padat (dense numerical vectors)
    yang merepresentasikan makna semantik teks untuk kalkulasi Cosine Similarity.
    """

    def __init__(self, n_features: int = 512):
        self.n_features = n_features
        self.vectorizer = HashingVectorizer(
            n_features=n_features,
            norm="l2",
            alternate_sign=False,
            ngram_range=(1, 2)
        )

    @staticmethod
    def name() -> str:
        return "fast_local_hashing"

    def get_config(self) -> dict:
        return {"n_features": self.n_features}

    @classmethod
    def build_from_config(cls, config: dict):
        return cls(n_features=config.get("n_features", 512))

    def __call__(self, input: Documents) -> Embeddings:
        matrix = self.vectorizer.transform(input)
        return matrix.toarray().tolist()


class VectorDBService:
    """
    Service ChromaDB untuk mengelola alur RAG:
    1. Chunking & Overlap dokumen panjang
    2. Embedding (Vektorisasi)
    3. Penyimpanan & Vector Retrieval (Top-K Similarity Search)
    """

    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Inisialisasi persistent client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Inisialisasi embedding function
        self.embedding_fn = self._get_embedding_function()

        # Ambil atau buat koleksi
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"description": "FAQ dan Knowledge Base Dea Trans Group (RAG Chunks)"}
        )
        
        # Inisialisasi data bawaan jika koleksi masih kosong
        self._seed_default_faqs_if_needed()

    def _get_embedding_function(self) -> EmbeddingFunction:
        """Memilih fungsi embedding semantik terbaik."""
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
            try:
                from chromadb.utils import embedding_functions
                logger.info("Menggunakan OpenAI Embedding Function untuk ChromaDB.")
                return embedding_functions.OpenAIEmbeddingFunction(
                    api_key=settings.OPENAI_API_KEY,
                    model_name="text-embedding-3-small"
                )
            except Exception as e:
                logger.warning(f"Gagal memuat OpenAI Embedding, beralih ke FastLocalEmbedding: {e}")

        logger.info("Menggunakan FastLocalEmbeddingFunction (Ultra-fast & Semantic Vectorization).")
        return FastLocalEmbeddingFunction()

    def _seed_default_faqs_if_needed(self):
        """
        Memasukkan data FAQ default ke ChromaDB dengan alur Chunking & Embedding.
        Setiap dokumen panjang dipecah menjadi chunks dengan irisan overlap.
        """
        try:
            count = self.collection.count()
            if count == 0:
                logger.info("Koleksi ChromaDB kosong. Memproses Chunking & Embedding data default Dea Trans...")
                all_chunks: List[TextChunk] = []

                for doc in DEA_TRANS_FAQ_DOCUMENTS:
                    chunks = text_chunker.chunk_document(
                        doc_id=doc["id"],
                        content=doc["content"],
                        title=doc["title"],
                        category=doc["category"],
                        source=doc["source"]
                    )
                    all_chunks.extend(chunks)

                ids = [f"{c.metadata['parent_id']}_c{c.chunk_index}" for c in all_chunks]
                documents = [c.text for c in all_chunks]
                metadatas = [c.to_dict() for c in all_chunks]

                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                logger.info(
                    f"Berhasil memotong {len(DEA_TRANS_FAQ_DOCUMENTS)} dokumen menjadi "
                    f"{len(ids)} chunks dan menyimpannya ke ChromaDB."
                )
            else:
                logger.info(f"Koleksi ChromaDB sudah berisi {count} chunks dokumen.")
        except Exception as e:
            logger.error(f"Gagal melakukan seeding ChromaDB: {e}", exc_info=True)

    def add_documents(self, docs: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Menambahkan dokumen baru dengan alur Chunking -> Embedding -> ChromaDB storage.
        Mengembalikan statistik jumlah dokumen asal dan total potongan (chunks) yang dibuat.
        """
        all_chunks: List[TextChunk] = []

        for doc in docs:
            doc_id = doc.get("id") or str(uuid.uuid4())
            chunks = text_chunker.chunk_document(
                doc_id=doc_id,
                content=doc["content"],
                title=doc.get("title", "Dokumen Baru"),
                category=doc.get("category", "Umum"),
                source=doc.get("source", "https://deatransgroup.com/")
            )
            all_chunks.extend(chunks)

        if not all_chunks:
            return {"inserted_documents": 0, "inserted_chunks": 0}

        ids = [f"{c.metadata['parent_id']}_c{c.chunk_index}_{uuid.uuid4().hex[:4]}" for c in all_chunks]
        contents = [c.text for c in all_chunks]
        metadatas = [c.to_dict() for c in all_chunks]

        self.collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas
        )

        logger.info(f"RAG Chunking: Berhasil menyimpan {len(docs)} dokumen ({len(ids)} chunks) ke ChromaDB.")
        return {
            "inserted_documents": len(docs),
            "inserted_chunks": len(ids)
        }

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Vector Retrieval (Pencarian Vektor):
        1. Query diubah menjadi vektor embedding semantik.
        2. ChromaDB mencari chunks dengan jarak vektor terdekat (Cosine Distance).
        3. Mengambil Top-K chunks paling relevan.
        """
        k = top_k or settings.RETRIEVAL_TOP_K
        total = self.collection.count()
        if total == 0:
            return []

        n_results = min(k, total)
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            formatted_results = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                ids = results["ids"][0] if results.get("ids") else [""] * len(docs)
                distances = results["distances"][0] if results.get("distances") else [1.0] * len(docs)

                for chunk_id, text, meta, dist in zip(ids, docs, metas, distances):
                    distance_val = float(dist)
                    # Konversi distance ke estimasi kemiripan Cosine Similarity (0 s/d 1)
                    relevance_score = max(0.0, min(1.0, 1.0 - (distance_val / 2.0)))

                    formatted_results.append({
                        "id": chunk_id,
                        "content": text,
                        "title": meta.get("title", "FAQ Dea Trans"),
                        "category": meta.get("category", "Umum"),
                        "source": meta.get("source", "https://deatransgroup.com/"),
                        "parent_id": meta.get("parent_id", ""),
                        "chunk_index": meta.get("chunk_index", 0),
                        "total_chunks": meta.get("total_chunks", 1),
                        "distance": distance_val,
                        "relevance_score": relevance_score
                    })

            return formatted_results
        except Exception as e:
            logger.error(f"Error saat query ke ChromaDB: {e}", exc_info=True)
            return []

    def is_knowledge_sufficient(self, search_results: List[Dict[str, Any]]) -> bool:
        """
        Evaluasi apakah chunks hasil retrieval memadai:
        - Harus ada setidaknya 1 chunk yang ditemukan.
        - Chunk terbaik memiliki distance <= threshold (skor kemiripan cukup tinggi).
        """
        if not search_results:
            return False

        best_result = search_results[0]
        best_distance = best_result.get("distance", 999.0)
        
        is_sufficient = best_distance <= settings.RETRIEVAL_DISTANCE_THRESHOLD
        logger.info(
            f"Evaluasi RAG: best_distance={best_distance:.4f}, "
            f"threshold={settings.RETRIEVAL_DISTANCE_THRESHOLD}, sufficient={is_sufficient}"
        )
        return is_sufficient

    def count(self) -> int:
        return self.collection.count()


# Singleton instance
vector_db_service = VectorDBService()
