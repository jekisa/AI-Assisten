import re
from typing import List, Dict, Any, Optional
from app.config import settings


class TextChunk:
    """Representasi satu potongan teks hasil chunking."""
    def __init__(
        self,
        text: str,
        chunk_index: int,
        total_chunks: int,
        metadata: Dict[str, Any]
    ):
        self.text = text
        self.chunk_index = chunk_index
        self.total_chunks = total_chunks
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        data = dict(self.metadata)
        data.update({
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "char_count": len(self.text)
        })
        return data


class TextChunker:
    """
    Pemotong teks (Chunking Engine) dengan teknik sliding window dan chunk overlap.
    Memastikan konteks makna antarkalimat tidak terputus saat teks panjang dipotong.
    """

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size or getattr(settings, "CHUNK_SIZE", 500)
        self.chunk_overlap = chunk_overlap or getattr(settings, "CHUNK_OVERLAP", 100)
        self.separators = separators or ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap harus lebih kecil daripada chunk_size")

    def split_text(self, text: str) -> List[str]:
        """
        Memotong teks menjadi list chunks dengan mempertimbangkan pemisah alami dan overlap.
        """
        text = text.strip()
        if not text:
            return []

        # Jika panjang teks sudah lebih kecil atau sama dengan chunk_size, kembalikan langsung
        if len(text) <= self.chunk_size:
            return [text]

        chunks: List[str] = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size

            if end >= text_len:
                # Sisa teks terakhir
                remaining = text[start:].strip()
                if remaining:
                    chunks.append(remaining)
                break

            # Cari titik potong terbaik (boundary) menggunakan separator alami
            slice_to_inspect = text[start:end]
            best_split = -1

            for sep in self.separators:
                idx = slice_to_inspect.rfind(sep)
                # Prioritaskan pemisah yang tidak terlalu dekat dengan start (> 30% dari chunk_size)
                if idx != -1 and idx > int(self.chunk_size * 0.3):
                    best_split = idx + len(sep)
                    break

            if best_split != -1:
                actual_end = start + best_split
            else:
                actual_end = end

            chunk_text = text[start:actual_end].strip()
            if chunk_text:
                chunks.append(chunk_text)

            # Geser start dengan memperhitungkan overlap
            step = (actual_end - start) - self.chunk_overlap
            if step <= 0:
                step = max(1, actual_end - start)

            start += step

        return chunks

    def chunk_document(
        self,
        doc_id: str,
        content: str,
        title: str,
        category: str = "Umum",
        source: str = "https://deatransgroup.com/",
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> List[TextChunk]:
        """
        Memotong satu dokumen utuh menjadi serangkaian TextChunk terindeks.
        """
        raw_chunks = self.split_text(content)
        total = len(raw_chunks)
        result: List[TextChunk] = []

        base_meta = {
            "parent_id": doc_id,
            "title": title,
            "category": category,
            "source": source
        }
        if extra_metadata:
            base_meta.update(extra_metadata)

        for i, c_text in enumerate(raw_chunks):
            chunk_obj = TextChunk(
                text=c_text,
                chunk_index=i,
                total_chunks=total,
                metadata=base_meta
            )
            result.append(chunk_obj)

        return result


# Singleton instance
text_chunker = TextChunker()

