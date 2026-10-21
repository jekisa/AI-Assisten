from typing import List, Dict, Any

SYSTEM_INSTRUCTION = """Kamu adalah Asisten AI Customer Service resmi Dea Trans Group (Website: https://deatransgroup.com/).
Tugas utamamu adalah menjawab pertanyaan pelanggan secara ramah, sopan, akurat, dan solutif (gunakan sapaan 'Kak' atau 'Kakak').

PRINSIP GROUNDEDNESS & ANTI-HALUSINASI:
1. Jawablah HANYA berdasarkan KONTEKS DOKUMEN yang disediakan di bawah ini.
2. Jangan mengarang informasi harga, nomor kontak, jadwal, atau ketentuan yang tidak ada di dalam konteks.
3. Jika informasi spesifik tidak ditemukan di dalam konteks dokumen, sampaikan dengan santun bahwa data tersebut belum tercantum dan sarankan untuk menghubungi Customer Care 24 Jam Dea Trans Group melalui website resmi https://deatransgroup.com/.
4. Sajikan jawaban yang terstruktur (gunakan poin/bullet list bila menjelaskan langkah atau kebijakan)."""


class PromptAugmenter:
    """
    Komponen Pengayaan Prompt (Prompt Augmentation) dalam arsitektur RAG.
    Menggabungkan pertanyaan asli user dengan konteks hasil retrieval Top-K chunks
    beserta metadata dokumen (judul, kategori, nomor chunk) ke dalam prompt terstruktur.
    """

    @staticmethod
    def build_augmented_messages(
        user_query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Menyusun array messages (system & user) yang kaya akan konteks dokumen rujukan.
        """
        # Susun blok konteks beranotasi
        context_blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            title = chunk.get("title", "Dokumen Informasi")
            category = chunk.get("category", "FAQ")
            source = chunk.get("source", "https://deatransgroup.com/")
            content = chunk.get("content", "").strip()
            score = chunk.get("relevance_score")
            score_str = f" | Skor Relevansi: {score:.2f}" if score is not None else ""
            chunk_info = f" | Bagian {chunk.get('chunk_index', 0) + 1} dari {chunk.get('total_chunks', 1)}" if "chunk_index" in chunk else ""

            block = (
                f"[DOKUMEN RUJUKAN {i}]\n"
                f"Judul: {title}\n"
                f"Kategori: {category}{chunk_info}{score_str}\n"
                f"Sumber URL: {source}\n"
                f"Isi Dokumen:\n{content}\n"
            )
            context_blocks.append(block)

        formatted_context = "\n----------------------------------------\n".join(context_blocks)

        augmented_system_prompt = (
            f"{SYSTEM_INSTRUCTION}\n\n"
            "====================================================\n"
            "KONTEKS INFORMASI HASIL VECTOR RETRIEVAL (TOP-K CHUNKS):\n"
            "====================================================\n"
            f"{formatted_context}\n"
            "====================================================\n"
            "Gunakan konteks di atas untuk menjawab pertanyaan pelanggan berikut."
        )

        return [
            {"role": "system", "content": augmented_system_prompt},
            {"role": "user", "content": user_query}
        ]


# Singleton instance
prompt_augmenter = PromptAugmenter()

