import pytest
from app.services.chunker import TextChunker, text_chunker
from app.services.vector_db import vector_db_service
from app.core.prompt_augmenter import prompt_augmenter
from app.core.agent import dea_trans_agent


def test_rag_stage_1_chunking_and_overlap():
    """
    Uji Tahap 1: Chunking (Pemotongan Teks) & Chunk Overlap.
    Memastikan dokumen panjang dipotong menjadi chunks kecil dan memiliki irisan (overlap).
    """
    chunker = TextChunker(chunk_size=120, chunk_overlap=30)
    
    long_text = (
        "Dea Trans Group menyediakan armada HiAce Premio untuk perjalanan Bandung Jakarta. "
        "Fasilitas lengkap meliputi AC dingin, kursi ergonomis yang dapat direbahkan, "
        "charger HP di setiap baris kursi, serta bagasi yang luas dan aman. "
        "Layanan door-to-door memastikan penjemputan langsung di depan pintu rumah Anda."
    )

    chunks = chunker.chunk_document(
        doc_id="test_doc_01",
        content=long_text,
        title="Fasilitas Armada HiAce",
        category="Armada"
    )

    # 1. Teks harus terpotong menjadi lebih dari 1 chunk
    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].total_chunks == len(chunks)
    assert chunks[0].metadata["parent_id"] == "test_doc_01"

    # 2. Periksa keberadaan overlap (irisan teks antara chunk 0 dan chunk 1)
    chunk_0_text = chunks[0].text
    chunk_1_text = chunks[1].text
    
    # Ambil beberapa kata dari ujung chunk 0 dan pastikan muncul di awal atau bagian dari chunk 1
    words_end_0 = chunk_0_text.split()[-3:]
    overlap_found = any(word in chunk_1_text for word in words_end_0)
    assert overlap_found is True, "Overlap kata tidak ditemukan di antara chunk bersebelahan"


def test_rag_stage_2_embedding_vectorization():
    """
    Uji Tahap 2: Embedding (Vektorisasi Semantik).
    Memastikan teks diubah menjadi representasi vektor numerik.
    """
    import numpy as np
    embedding_fn = vector_db_service.embedding_fn
    sample_texts = ["Kebijakan pengembalian barang", "Komisi afiliasi agen tiket travel"]
    vectors = embedding_fn(sample_texts)

    assert len(vectors) == 2
    assert isinstance(vectors[0], (list, tuple, np.ndarray))
    assert len(vectors[0]) > 0
    # Memastikan elemen vektor berupa float angka
    assert all(isinstance(float(v), float) for v in vectors[0][:10])


def test_rag_stage_3_vector_retrieval_top_k():
    """
    Uji Tahap 3: Vector Retrieval (Pencarian Vektor Top-K).
    Memastikan pertanyaan user mencari chunks dengan kemiripan Cosine tertinggi.
    """
    query = "Bagaimana prosedur klaim jika barang tertinggal di travel Dea Trans?"
    retrieved_chunks = vector_db_service.search(query, top_k=3)

    assert len(retrieved_chunks) <= 3
    assert len(retrieved_chunks) > 0

    best_chunk = retrieved_chunks[0]
    assert "content" in best_chunk
    assert "title" in best_chunk
    assert "distance" in best_chunk
    assert "relevance_score" in best_chunk
    # Relevansi dokumen harus terkait barang/bagasi
    assert any("barang" in c["title"].lower() or "bagasi" in c["title"].lower() for c in retrieved_chunks)


def test_rag_stage_4_prompt_augmentation():
    """
    Uji Tahap 4: Prompt Augmentation (Pengayaan Prompt).
    Memastikan potongan teks hasil retrieval digabungkan dengan pertanyaan user ke dalam wadah prompt.
    """
    user_query = "Berapa hari barang tertinggal disimpan di pool?"
    mock_chunks = [
        {
            "title": "Kebijakan Barang Tertinggal",
            "category": "Bagasi",
            "source": "https://deatransgroup.com/kebijakan-bagasi",
            "content": "Barang tertinggal disimpan aman di pool hingga maksimal 30 hari kalender.",
            "relevance_score": 0.92,
            "chunk_index": 0,
            "total_chunks": 1
        }
    ]

    messages = prompt_augmenter.build_augmented_messages(
        user_query=user_query,
        retrieved_chunks=mock_chunks
    )

    assert len(messages) == 2
    system_msg = messages[0]["content"]
    user_msg = messages[1]["content"]

    # 1. Pertanyaan asli ada di user prompt
    assert user_msg == user_query

    # 2. Konten chunk hasil retrieval ada di system prompt (augmented)
    assert "Barang tertinggal disimpan aman di pool hingga maksimal 30 hari" in system_msg
    assert "Kebijakan Barang Tertinggal" in system_msg
    assert "KONTEKS INFORMASI HASIL VECTOR RETRIEVAL" in system_msg


def test_rag_end_to_end_pipeline():
    """
    Uji Integrasi End-to-End RAG:
    User bertanya -> Router -> Vector Retrieval Top-K -> Prompt Augmentation -> Final Grounded Answer.
    """
    question = "Berapa komisi yang didapatkan mitra agen tiket Dea Trans?"
    response = dea_trans_agent.process_query(question)

    assert response.route_taken == "vector_retrieval"
    assert response.intent == "FAQ_KNOWLEDGE"
    assert len(response.sources) > 0
    # Jawaban akhir harus memuat informasi komisi yang ada di dokumen
    assert "komisi" in response.answer.lower() or "agen" in response.answer.lower()
