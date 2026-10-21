from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="Pertanyaan atau pesan dari pengguna", min_length=1)
    conversation_id: Optional[str] = Field(default=None, description="ID sesi percakapan jika ada")


class SourceItem(BaseModel):
    title: str = Field(..., description="Judul atau rujukan sumber")
    source: str = Field(..., description="URL atau nama dokumen sumber")
    category: Optional[str] = Field(default=None, description="Kategori dokumen")
    snippet: Optional[str] = Field(default=None, description="Ringkasan teks dari sumber")
    score: Optional[float] = Field(default=None, description="Relevansi skor / distance")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Jawaban resmi dari Asisten AI Dea Trans")
    route_taken: str = Field(..., description="Node keputusan yang diambil: direct_greeting | vector_retrieval | web_search_fallback")
    intent: str = Field(..., description="Niat yang terdeteksi oleh LLM Router: GREETING | FAQ_KNOWLEDGE | WEB_FALLBACK")
    sources: List[SourceItem] = Field(default_factory=list, description="Daftar sumber rujukan yang digunakan")
    execution_time_ms: Optional[float] = Field(default=None, description="Waktu eksekusi proses dalam milidetik")
    conversation_id: Optional[str] = Field(default=None, description="ID percakapan")


class DocumentItem(BaseModel):
    id: Optional[str] = Field(default=None, description="ID unik dokumen. Jika kosong akan digenerate otomatis")
    title: str = Field(..., description="Judul topik FAQ")
    category: str = Field(default="Umum", description="Kategori FAQ")
    content: str = Field(..., description="Isi materi informasi / SOP FAQ")
    source: str = Field(default="https://deatransgroup.com/", description="Tautan atau referensi sumber")


class IngestDocumentsRequest(BaseModel):
    documents: List[DocumentItem] = Field(..., description="Daftar dokumen FAQ yang ingin dimasukkan ke ChromaDB")


class IngestDocumentsResponse(BaseModel):
    status: str
    inserted_count: int
    inserted_chunks: Optional[int] = Field(default=None, description="Total potongan (chunks) yang dihasilkan dari pemotongan teks")
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    vector_db_connected: bool
    total_documents: int

