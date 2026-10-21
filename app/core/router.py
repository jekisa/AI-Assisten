import re
import logging
from typing import Literal
from app.core.llm import llm_client

logger = logging.getLogger(__name__)

IntentType = Literal["GREETING", "FAQ_KNOWLEDGE", "WEB_FALLBACK"]

ROUTER_SYSTEM_PROMPT = """Kamu adalah LLM Router klasifikasi niat (intent classifier) untuk Customer Service Dea Trans Group (https://deatransgroup.com/).
Tugasmu HANYA mengklasifikasikan pesan pengguna ke salah satu dari 3 kategori berikut:

1. GREETING:
   - Pengguna HANYA menyapa, memberi salam, bertanya kabar, berterima kasih, atau basa-basi singkat tanpa pertanyaan spesifik.
   - Contoh: "Halo", "Selamat pagi min", "Hai apa kabar?", "Assalamualaikum", "Terima kasih banyak".

2. FAQ_KNOWLEDGE:
   - Pengguna bertanya mengenai informasi operasional, layanan, atau kebijakan Dea Trans Group, khususnya:
     * Kebijakan pengembalian barang (barang tertinggal di travel, klaim ganti rugi paket hilang/rusak).
     * Komisi afiliasi, sistem mitra, pendaftaran agen tiket travel.
     * Jadwal, armada (HiAce, Innova), fasilitas travel, kebijakan refund & reschedule tiket, pengiriman paket kilat.
   - Contoh: "Bagaimana kebijakan pengembalian barang tertinggal di mobil?", "Berapa komisi afiliasi agen tiket Dea Trans?", "Apakah bisa reschedule tiket?", "Armada apa saja yang tersedia?".

3. WEB_FALLBACK:
   - Pengguna menanyakan informasi eksternal terkini di luar SOP internal, kondisi jalan tol/lalu lintas hari ini, berita terkini, atau informasi umum yang membutuhkan pencarian internet.
   - Contoh: "Apakah tol Cipali macet hari ini?", "Siapa pemilik deatrans?", "Berita kecelakaan travel hari ini".

ATURAN OUTPUT:
Jawab HANYA dengan satu kata persis: GREETING, FAQ_KNOWLEDGE, atau WEB_FALLBACK. Jangan tambahkan kata lain!"""


class IntentRouter:
    """
    Router berbasis LLM untuk menentukan jalur eksekusi percakapan pelanggan.
    """

    def __init__(self):
        self.llm = llm_client

    def classify_intent(self, message: str) -> IntentType:
        """
        Klasifikasikan niat pengguna menggunakan LLM Router.
        Jika LLM mengembalikan nilai tak terduga, lakukan heuristic fallback.
        """
        clean_msg = message.strip()
        if not clean_msg:
            return "GREETING"

        # Cek terlebih dahulu dengan fast-path regex untuk salam sangat umum
        # guna menghemat latency jika pertanyaan murni salam
        fast_greeting = self._check_fast_greeting(clean_msg)
        if fast_greeting:
            logger.info(f"Fast-path Router mendeteksi sapaan: '{clean_msg}' -> GREETING")
            return "GREETING"

        # Panggil LLM untuk klasifikasi akurat
        messages = [
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": clean_msg}
        ]

        try:
            raw_result = self.llm.generate_chat_completion(
                messages=messages,
                temperature=0.0,
                max_tokens=10
            ).strip().upper()

            logger.info(f"LLM Router classification response: '{raw_result}' for input: '{clean_msg}'")

            if "GREETING" in raw_result:
                return "GREETING"
            elif "FAQ_KNOWLEDGE" in raw_result:
                return "FAQ_KNOWLEDGE"
            elif "WEB_FALLBACK" in raw_result or "WEB" in raw_result:
                return "WEB_FALLBACK"

        except Exception as e:
            logger.error(f"Error saat LLM routing: {e}. Menggunakan rule-based classification.", exc_info=True)

        # Fallback Heuristik
        return self._heuristic_fallback_classification(clean_msg)

    def _check_fast_greeting(self, text: str) -> bool:
        """
        Deteksi cepat jika pesan adalah sapaan murni (tanpa pertanyaan teknis/transaksi).
        """
        t = text.lower().strip()
        # Bersihkan tanda baca di akhir kalimat
        clean_text = re.sub(r"[?!.,]+$", "", t).strip()

        # Daftar kata kunci teknis/transaksi yang tidak boleh dianggap sapaan murni
        transactional_keywords = [
            "barang", "hilang", "tertinggal", "komisi", "afiliasi", "agen",
            "tiket", "pesan", "booking", "harga", "tarif", "ongkir", "jadwal",
            "rute", "reschedule", "refund", "batal", "macet", "tol"
        ]
        if any(w in clean_text for w in transactional_keywords):
            return False

        # Pola umum sapaan murni
        greeting_patterns = [
            r"^(halo|hai|hi|hello|hei)(\s+min|\s+admin|\s+dea\s+trans)?(\s+apa\s+kabar)?(\s+hari\s+ini)?$",
            r"^(selamat|met)\s+(pagi|siang|sore|malam)(\s+min|\s+admin|\s+dea\s+trans)?(,\s*apa\s+kabar.*)?$",
            r"^(assalamu['\s]?alaikum|sampurasun|kulonuwun)",
            r"^(apa\s+kabar|gimana\s+kabarnya)(\s+min|\s+dea\s+trans)?(\s+hari\s+ini)?$",
            r"^(terima\s+kasih|makasih|thanks|thank\s+you)(\s+banyak|\s+min)?$",
            r"^(tes|test|ping|p)$"
        ]
        return any(re.search(p, clean_text) for p in greeting_patterns)

    def _heuristic_fallback_classification(self, text: str) -> IntentType:
        """
        Klasifikasi darurat menggunakan kata kunci bila LLM tidak merespon.
        """
        t = text.lower()
        faq_keywords = [
            "barang", "kembali", "tertinggal", "hilang", "rusak", "komisi", "afiliasi",
            "agen", "mitra", "tiket", "refund", "reschedule", "jadwal", "harga", "rute",
            "paket", "hiace", "innova", "travel", "shuttle", "biaya", "tarif", "batal"
        ]
        web_keywords = ["macet", "tol", "cuaca", "berita", "kecelakaan", "pendiri", "pemilik"]

        if any(w in t for w in faq_keywords):
            return "FAQ_KNOWLEDGE"
        if any(w in t for w in web_keywords):
            return "WEB_FALLBACK"
        return "GREETING"


# Singleton instance
router = IntentRouter()
