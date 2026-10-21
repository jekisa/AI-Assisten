from fastapi import APIRouter, HTTPException, status
from app.schemas import IngestDocumentsRequest, IngestDocumentsResponse
from app.services.vector_db import vector_db_service

router = APIRouter(prefix="/documents", tags=["Knowledge Base & Ingestion"])


@router.post(
    "",
    response_model=IngestDocumentsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Dokumen FAQ ke ChromaDB",
    description="Menyimpan dokumen pengetahuan baru ke Vector Database ChromaDB dengan alur Chunking, Overlap, dan Embedding."
)
async def ingest_documents(request: IngestDocumentsRequest) -> IngestDocumentsResponse:
    try:
        docs_to_insert = [doc.model_dump() for doc in request.documents]
        res = vector_db_service.add_documents(docs_to_insert)
        doc_count = res["inserted_documents"]
        chunk_count = res["inserted_chunks"]
        return IngestDocumentsResponse(
            status="success",
            inserted_count=doc_count,
            inserted_chunks=chunk_count,
            message=f"Berhasil memproses {doc_count} dokumen menjadi {chunk_count} chunks dan menyimpannya ke ChromaDB."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menambahkan dokumen ke ChromaDB: {str(e)}"
        )


@router.get(
    "/count",
    summary="Jumlah Dokumen FAQ di ChromaDB",
    description="Mengembalikan total dokumen FAQ yang tersimpan saat ini di koleksi ChromaDB."
)
async def get_document_count():
    try:
        count = vector_db_service.count()
        return {"total_documents": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menghitung dokumen: {str(e)}"
        )

