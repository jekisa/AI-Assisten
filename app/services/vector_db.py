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

logger = logging.getLogger(__name__)


class FastLocalEmbeddingFunction(EmbeddingFunction):
    """
    Embedding function lokal berbasis L2-normalized HashingVectorizer.
    Ultra-cepat (<1ms), mandiri, tidak membutuhkan download model ONNX dari internet,
    dan sangat andal untuk klasifikasi FAQ dan kalkulasi cosine similarity.
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
    Service ChromaDB untuk menyimpan dan mencari pengetahuan FAQ Dea Trans Group.
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
            metadata={"description": "FAQ dan Knowledge Base Dea Trans Group"}
        )
        
        # Inisialisasi data bawaan jika koleksi masih kosong
        self._seed_default_faqs_if_needed()

    def _get_embedding_function(self) -> EmbeddingFunction:
        """Memilih fungsi embedding terbaik."""
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

        logger.info("Menggunakan FastLocalEmbeddingFunction (Ultra-fast & Offline).")
        return FastLocalEmbeddingFunction()

    def _seed_default_faqs_if_needed(self):
        """Memasukkan knowledge base default jika koleksi belum memiliki dokumen."""
        try:
            count = self.collection.count()
            if count == 0:
                logger.info("Koleksi ChromaDB kosong. Memasukkan data FAQ bawaan Dea Trans Group...")
                ids = [doc["id"] for doc in DEA_TRANS_FAQ_DOCUMENTS]
                documents = [doc["content"] for doc in DEA_TRANS_FAQ_DOCUMENTS]
                metadatas = [
                    {
                        "title": doc["title"],
                        "category": doc["category"],
                        "source": doc["source"]
                    }
                    for doc in DEA_TRANS_FAQ_DOCUMENTS
                ]
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                logger.info(f"Berhasil menambahkan {len(ids)} dokumen default ke ChromaDB.")
            else:
                logger.info(f"Koleksi ChromaDB sudah berisi {count} dokumen.")
        except Exception as e:
            logger.error(f"Gagal melakukan seeding ChromaDB: {e}", exc_info=True)

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Mencari dokumen yang paling relevan dengan pertanyaan pengguna.
        Mengembalikan list dokumen beserta metadata dan distance.
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

                for doc_id, text, meta, dist in zip(ids, docs, metas, distances):
                    formatted_results.append({
                        "id": doc_id,
                        "content": text,
                        "title": meta.get("title", "FAQ Dea Trans"),
                        "category": meta.get("category", "Umum"),
                        "source": meta.get("source", "https://deatransgroup.com/"),
                        "distance": float(dist),
                        # Konversi distance ke similarity skor aproksimasi (0-1)
                        "relevance_score": max(0.0, min(1.0, 1.0 - (float(dist) / 2.0)))
                    })

            return formatted_results
        except Exception as e:
            logger.error(f"Error saat query ke ChromaDB: {e}", exc_info=True)
            return []

    def is_knowledge_sufficient(self, search_results: List[Dict[str, Any]]) -> bool:
        """
        Evaluasi apakah dokumen lokal di ChromaDB memadai:
        1. Harus ada setidaknya 1 hasil dokumen.
        2. Dokumen terbaik harus memiliki distance <= threshold (artinya relevansi cukup tinggi).
        """
        if not search_results:
            return False

        best_result = search_results[0]
        best_distance = best_result.get("distance", 999.0)
        
        # Jarak lebih kecil berarti kemiripan lebih tinggi
        is_sufficient = best_distance <= settings.RETRIEVAL_DISTANCE_THRESHOLD
        logger.info(
            f"Evaluasi ChromaDB: best_distance={best_distance:.4f}, "
            f"threshold={settings.RETRIEVAL_DISTANCE_THRESHOLD}, sufficient={is_sufficient}"
        )
        return is_sufficient

    def add_documents(self, docs: List[Dict[str, Any]]) -> int:
        """Menambahkan dokumen kustom ke ChromaDB."""
        ids = [doc.get("id") or str(uuid.uuid4()) for doc in docs]
        contents = [doc["content"] for doc in docs]
        metadatas = [
            {
                "title": doc.get("title", "Dokumen Baru"),
                "category": doc.get("category", "Umum"),
                "source": doc.get("source", "https://deatransgroup.com/")
            }
            for doc in docs
        ]

        self.collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas
        )
        return len(ids)

    def count(self) -> int:
        return self.collection.count()


# Singleton instance
vector_db_service = VectorDBService()
