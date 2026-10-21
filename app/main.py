import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.schemas import HealthResponse
from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router
from app.services.vector_db import vector_db_service

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.APP_DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("deatrans_assistant")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Event handler saat aplikasi startup dan shutdown."""
    logger.info("==============================================================")
    logger.info(f"🚀 Memulai {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("   Layanan AI FAQ Dea Trans Group (https://deatransgroup.com/)")
    logger.info(f"   ChromaDB Path: {settings.CHROMA_PERSIST_DIRECTORY}")
    logger.info(f"   Koleksi Terisi: {vector_db_service.count()} dokumen")
    logger.info("==============================================================")
    yield
    logger.info("Menutup Asisten AI Dea Trans Group. Sampai jumpa!")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API Asisten AI Cerdas untuk mengelola pertanyaan operasional pelanggan (FAQ) "
        "pada Website Resmi **Dea Trans Group** (https://deatransgroup.com/).\n\n"
        "### Alur Logika Keputusan (Decision Flow):\n"
        "1. **Routing**: LLM Router mengklasifikasikan niat pengguna.\n"
        "2. **Kondisi 1 (Direct Answer)**: Menjawab sapaan/kabar langsung tanpa akses database (hemat token & latency).\n"
        "3. **Kondisi 2 (Vector Retrieval)**: Mengambil konteks dari Vector Database (ChromaDB) untuk pertanyaan seputar kebijakan barang, komisi afiliasi, armada, dan SOP.\n"
        "4. **Kondisi 3 (Fallback Web Search)**: Secara mandiri beralih mencari informasi terkini di internet (Tavily API) jika dokumen lokal dinilai tidak memadai."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware agar frontend website https://deatransgroup.com/ dapat mengakses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")


@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="Cek Status Layanan Asisten AI"
)
async def health_check():
    """Memeriksa kesehatan server dan konektivitas Vector DB."""
    try:
        total_docs = vector_db_service.count()
        connected = True
    except Exception:
        total_docs = 0
        connected = False

    return HealthResponse(
        status="healthy" if connected else "degraded",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        vector_db_connected=connected,
        total_documents=total_docs
    )


@app.get("/", tags=["System"], summary="Root API Information")
async def root():
    return {
        "message": f"Selamat datang di {settings.APP_NAME}",
        "documentation": "/docs",
        "health": "/api/v1/health",
        "official_website": "https://deatransgroup.com/"
    }
