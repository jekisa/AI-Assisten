import time
import logging
from typing import Dict, Any, List
from app.core.router import router, IntentType
from app.core.llm import llm_client
from app.services.vector_db import vector_db_service
from app.services.web_search import web_search_service
from app.schemas import ChatResponse, SourceItem

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_CUSTOMER_SERVICE = """Kamu adalah Asisten AI Customer Service resmi untuk Dea Trans Group (Website: https://deatransgroup.com/).
Dea Trans Group adalah perusahaan transportasi dan logistik terkemuka yang menyediakan layanan:
- Travel Antarkota Door-to-Door & Shuttle Point-to-Point (Armada: Toyota HiAce Commuter & Premio, Innova Reborn)
- Carter Drop dan Rental Mobil Pariwisata
- Titipan Pengiriman Paket Kilat 1 Hari Sampai (Same Day Delivery)
- Program Kemitraan Agen & Komisi Afiliasi Tiket Travel

PANDUAN MENJAWAB:
1. Bersikaplah sangat ramah, sopan, profesional, dan solutif (Gunakan sapaan "Kak" atau "Kakak").
2. Berikan jawaban yang tepat, ringkas, dan jelas berdasarkan KONTEKS yang diberikan.
3. Selalu sebutkan website resmi https://deatransgroup.com/ jika relevan untuk pemesanan atau pendaftaran.
4. Jangan pernah mengarang informasi kebijakan di luar konteks yang diberikan. Jika informasi tidak ada di konteks, sampaikan dengan santun untuk menghubungi Customer Care 24 Jam Dea Trans."""


class DeaTransAgent:
    """
    Agen AI Operasional FAQ Dea Trans Group.
    Mengelola alur logika bersyarat (Conditional Decision Graph):
    1. Routing: LLM Router mengklasifikasikan niat pengguna.
    2. Kondisi 1 (Direct Answer): Salam/kabar -> langsung dijawab tanpa query DB.
    3. Kondisi 2 (Vector Retrieval): Kebijakan barang, komisi afiliasi, travel -> query ChromaDB.
    4. Kondisi 3 (Fallback): Jika dokumen ChromaDB tidak memadai -> mandiri beralih ke Web Search (Tavily API).
    """

    def __init__(self):
        self.router = router
        self.llm = llm_client
        self.vector_db = vector_db_service
        self.web_search = web_search_service

    def process_query(self, message: str, conversation_id: str = None) -> ChatResponse:
        start_time = time.time()
        logger.info(f"[Agent] Memulai pemrosesan pesan: '{message}' (Conversation: {conversation_id})")

        # -------------------------------------------------------------
        # LANGKAH 1: ROUTING (LLM Router Decision Node)
        # -------------------------------------------------------------
        intent = self.router.classify_intent(message)
        logger.info(f"[Agent Node 1 - Router] Intent terdeteksi: {intent}")

        # -------------------------------------------------------------
        # KONDISI 1: DIRECT ANSWER (Hemat Token & Waktu Respons)
        # -------------------------------------------------------------
        if intent == "GREETING":
            logger.info("[Agent Node 2 - Direct Answer] Menjawab langsung tanpa memicu pencarian database.")
            answer = self._handle_direct_greeting(message)
            exec_time = (time.time() - start_time) * 1000

            return ChatResponse(
                answer=answer,
                route_taken="direct_greeting",
                intent=intent,
                sources=[],
                execution_time_ms=round(exec_time, 2),
                conversation_id=conversation_id
            )

        # -------------------------------------------------------------
        # KONDISI 2: VECTOR RETRIEVAL (ChromaDB)
        # -------------------------------------------------------------
        if intent == "FAQ_KNOWLEDGE":
            logger.info("[Agent Node 3 - Vector Retrieval] Memicu pencarian di ChromaDB...")
            vector_docs = self.vector_db.search(message)
            is_sufficient = self.vector_db.is_knowledge_sufficient(vector_docs)

            if is_sufficient:
                logger.info("[Agent Node 3 - Vector Retrieval] Dokumen di ChromaDB MEMADAI. Menghasilkan jawaban dari RAG.")
                answer = self._generate_answer_from_context(message, vector_docs, source_type="vector")
                
                sources = [
                    SourceItem(
                        title=doc.get("title", "Dokumen FAQ"),
                        source=doc.get("source", "https://deatransgroup.com/"),
                        category=doc.get("category", "FAQ"),
                        snippet=doc.get("content", "")[:200] + "...",
                        score=round(doc.get("relevance_score", 0.0), 3)
                    )
                    for doc in vector_docs
                ]
                
                exec_time = (time.time() - start_time) * 1000
                return ChatResponse(
                    answer=answer,
                    route_taken="vector_retrieval",
                    intent=intent,
                    sources=sources,
                    execution_time_ms=round(exec_time, 2),
                    conversation_id=conversation_id
                )
            else:
                logger.warning(
                    "[Agent Node 3 -> Node 4] Dokumen di database lokal TIDAK MEMADAI. "
                    "Secara mandiri memutuskan beralih ke Fallback Web Search!"
                )

        # -------------------------------------------------------------
        # KONDISI 3: FALLBACK (Web Search via Tavily API)
        # -------------------------------------------------------------
        logger.info("[Agent Node 4 - Fallback] Memicu Web Search Tool (Tavily API)...")
        web_results = self.web_search.search(message)
        answer = self._generate_answer_from_web(message, web_results)

        sources = [
            SourceItem(
                title=item.get("title", "Hasil Web"),
                source=item.get("url", "https://deatransgroup.com/"),
                category="Web Search",
                snippet=item.get("content", "")[:200] + "...",
                score=round(item.get("score", 0.7), 3)
            )
            for item in web_results
        ]

        exec_time = (time.time() - start_time) * 1000
        return ChatResponse(
            answer=answer,
            route_taken="web_search_fallback",
            intent=intent,
            sources=sources,
            execution_time_ms=round(exec_time, 2),
            conversation_id=conversation_id
        )

    def _handle_direct_greeting(self, message: str) -> str:
        """Kondisi 1: Menghasilkan sapaan ramah langsung oleh LLM."""
        messages = [
            {
                "role": "system",
                "content": (
                    f"{SYSTEM_PROMPT_CUSTOMER_SERVICE}\n\n"
                    "Instruksi: Pengguna hanya menyapa atau menanyakan kabar. Balaslah dengan ramah, hangat, ceria, "
                    "dan tanyakan bagaimana Anda bisa membantu perjalanan travel atau urusan kiriman mereka hari ini. "
                    "Jawab secara singkat (1-3 kalimat)."
                )
            },
            {"role": "user", "content": message}
        ]
        return self.llm.generate_chat_completion(messages, temperature=0.6)

    def _generate_answer_from_context(self, question: str, docs: List[Dict[str, Any]], source_type: str = "vector") -> str:
        """Kondisi 2: Menghasilkan jawaban berdasarkan dokumen ChromaDB."""
        context_parts = []
        for i, d in enumerate(docs, 1):
            title = d.get("title", "")
            content = d.get("content", "")
            context_parts.append(f"--- DOKUMEN {i}: {title} ---\n{content}")

        context_str = "\n\n".join(context_parts)

        messages = [
            {
                "role": "system",
                "content": (
                    f"{SYSTEM_PROMPT_CUSTOMER_SERVICE}\n\n"
                    f"KONTEKS INFORMASI DARI DATABASE INTERNAL DEA TRANS:\n{context_str}\n\n"
                    "Instruksi: Jawablah pertanyaan pelanggan secara komprehensif, akurat, dan terstruktur sesuai konteks di atas. "
                    "Jika pertanyaan menyinggung kebijakan pengembalian barang, sebutkan batas waktu pelaporan (1x24 jam), masa simpan (30 hari), "
                    "dan syarat bukti booking. Jika menyinggung komisi afiliasi, sebutkan komisi per seat (Rp 15.000 - Rp 25.000 atau 10%-15%), "
                    "jadwal pencairan mingguan (hari Senin), dan link https://deatransgroup.com/."
                )
            },
            {"role": "user", "content": question}
        ]
        return self.llm.generate_chat_completion(messages, temperature=0.2)

    def _generate_answer_from_web(self, question: str, web_results: List[Dict[str, Any]]) -> str:
        """Kondisi 3: Menghasilkan jawaban berdasarkan hasil Web Search (Tavily)."""
        context_parts = []
        for i, res in enumerate(web_results, 1):
            title = res.get("title", "")
            url = res.get("url", "")
            content = res.get("content", "")
            context_parts.append(f"--- SUMBER WEB {i}: {title} ({url}) ---\n{content}")

        context_str = "\n\n".join(context_parts)

        messages = [
            {
                "role": "system",
                "content": (
                    f"{SYSTEM_PROMPT_CUSTOMER_SERVICE}\n\n"
                    f"KONTEKS DARI PENCARIAN WEB INTERNET TERKINI:\n{context_str}\n\n"
                    "Instruksi: Dokumen internal tidak memadai sehingga sistem mencari informasi terkini di internet. "
                    "Rangkum informasi dengan jelas, objektif, dan tetap dalam tone Customer Care Dea Trans Group. "
                    "Sertakan catatan bahwa penumpang dapat menghubungi Call Center/WhatsApp resmi Dea Trans Group "
                    "di https://deatransgroup.com/ untuk konfirmasi realtime."
                )
            },
            {"role": "user", "content": question}
        ]
        return self.llm.generate_chat_completion(messages, temperature=0.3)


# Singleton instance
dea_trans_agent = DeaTransAgent()
