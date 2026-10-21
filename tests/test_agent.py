import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.agent import dea_trans_agent
from app.services.vector_db import vector_db_service

client = TestClient(app)


def test_health_check_endpoint():
    """Uji endpoint health check dan koneksi ChromaDB."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["vector_db_connected"] is True
    assert data["total_documents"] >= 5


def test_root_endpoint():
    """Uji endpoint root."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Dea Trans Group" in data["message"]
    assert data["documentation"] == "/docs"


def test_kondisi_1_direct_answer_greeting():
    """
    Kondisi 1 (Direct Answer):
    Jika pengguna hanya menyapa atau bertanya kabar, LLM langsung menjawab
    tanpa memicu pencarian database lokal atau web search.
    """
    greetings = [
        "Halo min!",
        "Selamat pagi, apa kabar?",
        "Hai Dea Trans, apa kabar hari ini?"
    ]

    for msg in greetings:
        res = dea_trans_agent.process_query(msg)
        assert res.route_taken == "direct_greeting"
        assert res.intent == "GREETING"
        assert len(res.sources) == 0  # Tidak memicu query DB/Web
        assert len(res.answer) > 0


def test_kondisi_2_vector_retrieval_kebijakan_barang():
    """
    Kondisi 2 (Vector Retrieval):
    Jika pengguna bertanya tentang kebijakan pengembalian barang,
    agen secara otomatis memicu tool pencarian konteks di Vector Database (ChromaDB).
    """
    query = "Bagaimana kebijakan pengembalian barang yang tertinggal di travel?"
    res = dea_trans_agent.process_query(query)
    
    assert res.route_taken == "vector_retrieval"
    assert res.intent == "FAQ_KNOWLEDGE"
    assert len(res.sources) > 0
    # Memastikan salah satu sumber memuat topik barang / bagasi
    titles = [s.title.lower() for s in res.sources]
    assert any("barang" in t or "bagasi" in t or "dea trans" in t for t in titles)


def test_kondisi_2_vector_retrieval_komisi_afiliasi():
    """
    Kondisi 2 (Vector Retrieval):
    Jika pengguna bertanya tentang komisi afiliasi agen tiket Dea Trans,
    agen mencari konteks di ChromaDB.
    """
    query = "Berapa komisi afiliasi dan keuntungan menjadi agen tiket Dea Trans?"
    res = dea_trans_agent.process_query(query)
    
    assert res.route_taken == "vector_retrieval"
    assert res.intent == "FAQ_KNOWLEDGE"
    assert len(res.sources) > 0
    titles = [s.title.lower() for s in res.sources]
    assert any("afiliasi" in t or "mitra" in t or "agen" in t for t in titles)


def test_kondisi_3_fallback_web_search():
    """
    Kondisi 3 (Fallback):
    Jika dokumen di database lokal tidak memadai atau pengguna menanyakan situasi terkini,
    agen secara mandiri memutuskan untuk menggunakan tool Web Search.
    """
    query = "Apakah jalan tol Cipali arah Jakarta macet parah siang hari ini?"
    res = dea_trans_agent.process_query(query)
    
    assert res.route_taken == "web_search_fallback"
    assert len(res.sources) > 0
    assert res.sources[0].category == "Web Search"


def test_chat_api_endpoint():
    """Uji integrasi HTTP POST /api/v1/chat."""
    payload = {
        "message": "Halo, saya mau tanya soal komisi agen Dea Trans",
        "conversation_id": "conv-test-123"
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["route_taken"] in ["vector_retrieval", "direct_greeting", "web_search_fallback"]
    assert data["conversation_id"] == "conv-test-123"


def test_document_ingestion_api():
    """Uji penambahan FAQ dinamis via endpoint /api/v1/documents."""
    import uuid
    initial_count = vector_db_service.count()
    test_id = f"faq_test_{uuid.uuid4().hex[:8]}"

    new_doc_payload = {
        "documents": [
            {
                "id": test_id,
                "title": "Promo Diskon Mudik Dea Trans",
                "category": "Promo",
                "content": "Dea Trans Group memberikan diskon early bird mudik lebaran sebesar 20% untuk pemesanan H-30.",
                "source": "https://deatransgroup.com/promo-lebaran"
            }
        ]
    }
    
    response = client.post("/api/v1/documents", json=new_doc_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["inserted_count"] == 1
    
    # Cek jumlah dokumen bertambah
    assert vector_db_service.count() == initial_count + 1
