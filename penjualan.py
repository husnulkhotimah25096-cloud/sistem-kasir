"""Class Penjualan: rekap transaksi yang berhasil dan laporan penjualan."""


class Penjualan:
    def __init__(self):
        self.__daftar_penjualan = []
        self.__total_pendapatan = 0.0

    def get_daftar_penjualan(self):
        return list(self.__daftar_penjualan)

    def get_total_pendapatan(self):
        return self.__total_pendapatan

    def simpan_transaksi(self, transaksi):
        """Menyimpan transaksi yang sudah berhasil dibayar."""
        if not transaksi.sudah_selesai():
            raise ValueError("Hanya transaksi yang sudah dibayar yang dapat disimpan.")
        for t in self.__daftar_penjualan:
            if t.get_id_transaksi() == transaksi.get_id_transaksi():
                raise ValueError("Transaksi ini sudah tersimpan.")
        self.__daftar_penjualan.append(transaksi)
        self.__total_pendapatan += transaksi.get_total()

    def tampilkan_riwayat_penjualan(self):
        """Mengembalikan list teks, satu entri per transaksi."""
        riwayat = []
        for t in self.__daftar_penjualan:
            pelanggan = t.get_pelanggan()
            nama = pelanggan.get_nama() if pelanggan else "Umum"
            waktu = t.get_tanggal_transaksi().strftime("%Y-%m-%d %H:%M:%S")
            riwayat.append(f"{t.get_id_transaksi()} | {waktu} | {nama} | Rp{t.get_total():,.0f}")
        return riwayat

    def hitung_total_pendapatan(self):
        total = 0.0
        for t in self.__daftar_penjualan:
            total += t.get_total()
        self.__total_pendapatan = total
        return total

    def hitung_jumlah_transaksi(self):
        return len(self.__daftar_penjualan)

    def buat_laporan_penjualan(self):
        """Laporan berupa dict: jumlah transaksi, pendapatan, dan buku terjual."""
        buku_terjual = {}
        for t in self.__daftar_penjualan:
            for detail in t.get_daftar_detail():
                judul = detail.get_buku().get_judul()
                buku_terjual[judul] = buku_terjual.get(judul, 0) + detail.get_jumlah()
        return {
            "jumlah_transaksi": self.hitung_jumlah_transaksi(),
            "total_pendapatan": self.hitung_total_pendapatan(),
            "buku_terjual": buku_terjual,
        }

    def cetak_laporan(self):
        lap = self.buat_laporan_penjualan()
        baris = ["=" * 40, "   LAPORAN PENJUALAN LITERA HOUSE", "=" * 40,
                 f"Jumlah transaksi : {lap['jumlah_transaksi']}",
                 f"Total pendapatan : Rp{lap['total_pendapatan']:,.0f}",
                 "Buku terjual:"]
        for judul, jml in lap["buku_terjual"].items():
            baris.append(f"  - {judul}: {jml}")
        baris.append("=" * 40)
        return "\n".join(baris)