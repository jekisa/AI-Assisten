"""
Knowledge Base Default untuk Dea Trans Group (https://deatransgroup.com/)
Mencakup kebijakan pengembalian barang, komisi afiliasi & agen, layanan travel, dan SOP operasional.
"""

from typing import List, Dict

DEA_TRANS_FAQ_DOCUMENTS: List[Dict[str, str]] = [
    {
        "id": "faq_kebijakan_barang_tertinggal",
        "title": "Kebijakan Pengembalian Barang Tertinggal di Armada",
        "category": "Kebijakan Barang & Bagasi",
        "content": (
            "Kebijakan Pengembalian Barang Tertinggal di Armada Dea Trans Group:\n"
            "1. Jika barang penumpang tertinggal di dalam unit armada travel atau shuttle Dea Trans, "
            "segera hubungi Call Center / Customer Care resmi Dea Trans melalui WhatsApp di nomor operasional "
            "atau mendatangi pool/titik keberangkatan terdekat maksimal 1x24 jam setelah perjalanan.\n"
            "2. Penumpang wajib menyertakan bukti pemesanan tiket (Kode Booking), nama driver/nomor lambung armada "
            "jika mengingatnya, rute keberangkatan, waktu perjalanan, serta deskripsi spesifik barang yang tertinggal.\n"
            "3. Dea Trans Group akan mengamankan barang yang ditemukan di pool operasional. Barang tertinggal "
            "disimpan aman hingga maksimal 30 hari kalender. Jika tidak ada klaim setelah 30 hari, Dea Trans "
            "berhak mengelola atau mendonasikan barang tersebut.\n"
            "4. Pengambilan barang dapat dilakukan langsung di Pool terdekat tanpa biaya, atau dikirimkan kembali "
            "ke alamat pemilik melalui jasa kurir/ekspedisi dengan ongkos kirim ditanggung oleh pemilik barang."
        ),
        "source": "https://deatransgroup.com/kebijakan-bagasi-barang"
    },
    {
        "id": "faq_kebijakan_paket_rusak_hilang",
        "title": "Kebijakan Pengembalian dan Ganti Rugi Kiriman Paket Barang",
        "category": "Kebijakan Pengembalian Barang & Ekspedisi",
        "content": (
            "Kebijakan Pengembalian, Retur, dan Ganti Rugi Paket Barang Kilat Dea Trans Group:\n"
            "1. Pengembalian Barang (Retur Kiriman): Jika alamat penerima tidak ditemukan atau penerima menolak paket, "
            "paket akan disimpan di pool tujuan maksimal 7 hari dan diinformasikan ke pengirim. Pengembalian ke kota asal "
            "akan dikenakan biaya retur sebesar 50% dari ongkir awal.\n"
            "2. Klaim Kehilangan atau Kerusakan: Apabila terjadi kerusakan parah atau kehilangan paket yang disebabkan "
            "kelalaian operasional Dea Trans, pihak pengirim berhak mengajukan klaim ganti rugi maksimal 3x24 jam "
            "setelah status paket dinyatakan selesai/tiba.\n"
            "3. Besaran Ganti Rugi: Ganti rugi untuk paket non-asuransi maksimal adalah senilai 5x biaya ongkos kirim atau "
            "maksimal Rp 1.000.000,-. Untuk barang bernilai tinggi (elektronik, perhiasan, dokumen penting), pengirim "
            "wajib menggunakan asuransi pengiriman tambahan agar dicover 100% sesuai nilai deklarasi barang."
        ),
        "source": "https://deatransgroup.com/layanan-kirim-paket"
    },
    {
        "id": "faq_komisi_afiliasi_dan_keagenan",
        "title": "Program Komisi Afiliasi dan Mitra Agen Tiket Dea Trans",
        "category": "Kemitraan & Afiliasi",
        "content": (
            "Program Komisi Afiliasi dan Kemitraan Agen Dea Trans Group:\n"
            "1. Dea Trans Group membuka kesempatan kerjasama untuk perorangan, tour & travel, serta pemilik loket "
            "sebagai Agen Resmi atau Afiliator Tiket Perjalanan.\n"
            "2. Besaran Komisi Afiliasi & Penjualan Tiket:\n"
            "   - Komisi penjualan tiket travel/shuttle berkisar antara Rp 15.000 hingga Rp 25.000 per seat per penumpang "
            "tergantung rute yang dilayani (atau setara komisi 10% - 15% dari harga tiket reguler).\n"
            "   - Untuk rental mobil / carter drop armada (HiAce, Elf, Innova), mitra mendapatkan fee komisi mulai dari "
            "Rp 100.000 hingga Rp 300.000 per booking yang berhasil (deal).\n"
            "   - Komisi titipan pengiriman paket kilat sebesar 15% dari total ongkos kirim.\n"
            "3. Syarat & Pendaftaran:\n"
            "   - Mendaftar via menu Kemitraan di website resmi https://deatransgroup.com/ atau kontak PIC Kemitraan.\n"
            "   - Memiliki rekening bank aktif atas nama sendiri/perusahaan dan nomor WhatsApp aktif.\n"
            "4. Sistem Pembayaran Komisi:\n"
            "   - Komisi dihitung otomatis melalui dashboard mitra/agen.\n"
            "   - Pencairan dana komisi (withdraw) dilakukan setiap hari Senin (mingguan) dengan minimal penarikan Rp 50.000, "
            "langsung ditransfer ke rekening bank mitra tanpa potongan biaya administrasi tersembunyi."
        ),
        "source": "https://deatransgroup.com/program-afiliasi-mitra"
    },
    {
        "id": "faq_kebijakan_refund_reschedule",
        "title": "Kebijakan Pembatalan (Refund) dan Reschedule Tiket",
        "category": "Kebijakan Reservasi",
        "content": (
            "Ketentuan Reschedule dan Pengembalian Dana (Refund) Tiket Dea Trans Group:\n"
            "1. Perubahan Jadwal (Reschedule):\n"
            "   - Dapat dilakukan maksimal 12 jam sebelum waktu keberangkatan yang tertera di tiket.\n"
            "   - Perubahan jadwal pertama kali tidak dikenakan biaya administrasi (bebas biaya), selama kursi pada jadwal baru masih tersedia.\n"
            "   - Jika terdapat perbedaan tarif pada tanggal/jadwal baru, penumpang wajib membayar selisih harga.\n"
            "2. Pembatalan Tiket (Refund):\n"
            "   - Pembatalan lebih dari 24 jam sebelum jam keberangkatan: Pengembalian dana 75% dari harga tiket.\n"
            "   - Pembatalan antara 6 hingga 24 jam sebelum keberangkatan: Pengembalian dana 50% dari harga tiket.\n"
            "   - Pembatalan kurang dari 6 jam sebelum keberangkatan atau tidak hadir saat penjemputan (No-Show): Tiket hangus, dana tidak dapat dikembalikan.\n"
            "3. Proses pencairan dana refund diproses dalam waktu 3 hingga 7 hari kerja ke rekening pemesan tiket."
        ),
        "source": "https://deatransgroup.com/kebijakan-refund"
    },
    {
        "id": "faq_layanan_dan_fasilitas_armada",
        "title": "Layanan Utama dan Fasilitas Armada Dea Trans",
        "category": "Layanan & Armada",
        "content": (
            "Layanan dan Fasilitas Armada Dea Trans Group:\n"
            "1. Layanan Utama: Travel Door-to-Door, Shuttle Point-to-Point, Carter Drop Antarkota, Rental Mobil Pariwisata, "
            "dan Pengiriman Titipan Paket Kilat Satu Hari Sampai (Same Day Delivery).\n"
            "2. Armada yang Digunakan: Toyota HiAce Commuter & Premio, Toyota Innova Reborn/Zenix, dan Isuzu Elf Long Executive.\n"
            "3. Fasilitas di Dalam Armada: Full Air Conditioner (AC), Reclining Seat (kursi ergonomis dapat direbahkan), "
            "USB/Type-C Phone Charging Port di setiap baris, bagasi luas, audio/video entertainment, serta driver berpengalaman dan tersertifikasi.\n"
            "4. Reservasi Tiket: Pemesanan tiket dapat dilakukan secara online 24 jam melalui website resmi https://deatransgroup.com/ "
            "atau via WhatsApp Customer Service resmi Dea Trans."
        ),
        "source": "https://deatransgroup.com/tentang-kami"
    }
]
