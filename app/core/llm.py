import logging
from typing import List, Dict, Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Klien universal untuk interaksi dengan Large Language Model (OpenAI API / OpenAI-Compatible).
    Memiliki mekanisme cerdas (smart fallback) jika API key belum diset.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.client = None

        if self.api_key and self.api_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=settings.OPENAI_BASE_URL
                )
                logger.info(f"OpenAI Client berhasil diinisialisasi dengan model '{self.model}'.")
            except Exception as e:
                logger.warning(f"Gagal menginisialisasi OpenAI Client: {e}")
        else:
            logger.info("OPENAI_API_KEY belum dikonfigurasi. Menggunakan Smart LLM Fallback Engine.")

    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 800
    ) -> str:
        """
        Menghasilkan teks completion dari LLM.
        """
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"Error memanggil OpenAI API: {e}. Mengalihkan ke Smart Fallback Generator.")

        # Fallback jika client tidak ada atau error API
        return self._generate_smart_fallback(messages)

    def _generate_smart_fallback(self, messages: List[Dict[str, str]]) -> str:
        """
        Smart text generator yang menghasilkan format jawaban profesional
        Customer Service Dea Trans Group jika API eksternal belum dihubungkan.
        """
        last_user_message = ""
        system_prompt = ""
        for m in messages:
            if m.get("role") == "user":
                last_user_message = m.get("content", "")
            elif m.get("role") == "system":
                system_prompt = m.get("content", "")

        q_lower = last_user_message.lower()

        # 1. Jika pemanggilan berasal dari LLM Router (permintaan klasifikasi niat)
        if "llm router" in system_prompt.lower() or "klasifikasi niat" in system_prompt.lower():
            # Cek apakah pertanyaan seputar operasional/FAQ internal Dea Trans
            faq_terms = [
                "barang", "tertinggal", "hilang", "rusak", "komisi", "afiliasi", "agen",
                "mitra", "tiket", "refund", "reschedule", "jadwal", "harga", "rute",
                "paket", "hiace", "innova", "travel", "shuttle", "biaya", "tarif", "batal",
                "kembali", "pengembalian", "bagasi", "kirim"
            ]
            web_terms = ["macet", "tol cipali", "tol trans jawa", "cuaca", "berita", "kecelakaan", "pemilik", "pendiri"]

            if any(term in q_lower for term in faq_terms):
                return "FAQ_KNOWLEDGE"
            elif any(term in q_lower for term in web_terms):
                return "WEB_FALLBACK"
            else:
                return "GREETING"

        # 2. Ekstraksi konteks jika ada di system prompt (RAG atau Web Search response generation)
        context = ""
        if "KONTEKS INFORMASI" in system_prompt:
            parts = system_prompt.split("KONTEKS INFORMASI")
            if len(parts) > 1:
                context = parts[1].strip()
        elif "KONTEKS DARI PENCARIAN WEB" in system_prompt:
            parts = system_prompt.split("KONTEKS DARI PENCARIAN WEB")
            if len(parts) > 1:
                context = parts[1].strip()

        # Jika ada konteks (dari ChromaDB atau Web Search), rangkum dengan gaya ramah CS Dea Trans
        if context:
            # Bersihkan instruksi di bagian akhir konteks jika ada
            clean_context = context.split("Instruksi:")[0].strip()
            return (
                f"Halo Kak! Terima kasih telah menghubungi Customer Care Dea Trans Group (https://deatransgroup.com/). "
                f"Mengenai pertanyaan Kakak seputar '{last_user_message}', berikut informasinya:\n\n"
                f"{clean_context}\n\n"
                f"Apakah ada informasi lain seputar perjalanan travel, kiriman paket, atau kemitraan kami yang bisa dibantu kembali Kak? 😊"
            )

        # 3. Direct answer sapaan
        if any(w in q_lower for w in ["halo", "hai", "selamat", "pagi", "siang", "sore", "malam", "kabar", "assalamualaikum"]):
            return (
                "Halo Kak! Selamat datang di Layanan Pelanggan Dea Trans Group (https://deatransgroup.com/). "
                "Kabar kami sangat baik dan siap melayani kebutuhan perjalanan travel, rental mobil, pengiriman paket kilat, "
                "maupun info kemitraan agen Kakak. Ada yang bisa kami bantu hari ini? 😊"
            )

        return (
            "Terima kasih telah menghubungi Dea Trans Group. "
            "Untuk informasi lebih lanjut dan pemesanan tiket resmi, silakan kunjungi website kami di "
            "https://deatransgroup.com/ atau hubungi Customer Care 24 Jam kami."
        )


# Singleton instance
llm_client = LLMClient()
