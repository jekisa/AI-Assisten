from fastapi import APIRouter, HTTPException, status
from app.schemas import ChatRequest, ChatResponse
from app.core.agent import dea_trans_agent

router = APIRouter(prefix="/chat", tags=["Chat & FAQ Assistant"])


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Kirim Pertanyaan ke Asisten AI Dea Trans Group",
    description=(
        "Endpoint utama pemrosesan FAQ dengan alur logika bersyarat:\n"
        "1. **Routing**: Mengklasifikasikan niat pengguna.\n"
        "2. **Direct Answer**: Menjawab langsung sapaan tanpa akses database.\n"
        "3. **Vector Retrieval**: Mengambil konteks dari ChromaDB jika seputar kebijakan/afiliasi/SOP.\n"
        "4. **Web Search Fallback**: Menggunakan Tavily API jika dokumen database lokal tidak memadai."
    )
)
async def chat_with_assistant(request: ChatRequest) -> ChatResponse:
    try:
        response = dea_trans_agent.process_query(
            message=request.message,
            conversation_id=request.conversation_id
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan saat memproses pertanyaan: {str(e)}"
        )

