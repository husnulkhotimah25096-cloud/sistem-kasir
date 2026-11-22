"""Class Transaksi: keranjang, pembayaran, dan struk."""
from datetime import datetime

from detail_transaksi import DetailTransaksi
from exceptions import PembayaranKurangError, StokTidakCukupError

DRAFT = "Draft"
SELESAI = "Selesai"
DIBATALKAN = "Dibatalkan"


class Transaksi:
    def __init__(self, id_transaksi, pelanggan=None):
        self.__id_transaksi = id_transaksi
        self.__tanggal_transaksi = datetime.now()
        self.__pelanggan = pelanggan  # objek Pelanggan, boleh None (pelanggan umum)
        self.__daftar_detail = []
        self.__total = 0.0
        self.__uang_bayar = 0.0
        self.__kembalian = 0.0
        self.__status_transaksi = DRAFT

    @classmethod
    def buat_transaksi(cls, id_transaksi, pelanggan=None):
        """Membuat transaksi baru berstatus Draft."""
        return cls(id_transaksi, pelanggan)

    # ---- Getter ----
    def get_id_transaksi(self):
        return self.__id_transaksi

    def get_tanggal_transaksi(self):
        return self.__tanggal_transaksi

    def get_pelanggan(self):
        return self.__pelanggan

    def get_daftar_detail(self):
        return list(self.__daftar_detail)

    def get_total(self):
        return self.__total

    def get_uang_bayar(self):
        return self.__uang_bayar

    def get_kembalian(self):
        return self.__kembalian

    def get_status(self):
        return self.__status_transaksi

    def sudah_selesai(self):
        return self.__status_transaksi == SELESAI

    def __pastikan_draft(self):
        if self.__status_transaksi != DRAFT:
            raise ValueError(f"Transaksi berstatus {self.__status_transaksi}, tidak dapat diubah.")

    # ---- Pelanggan dan keranjang ----
    def pilih_pelanggan(self, pelanggan):
        self.__pastikan_draft()
        self.__pelanggan = pelanggan

    def tambah_detail_transaksi(self, buku, jumlah):
        """Menambah buku ke keranjang; jumlah digabung bila bukunya sudah ada."""
        self.__pastikan_draft()
        if jumlah <= 0:
            raise ValueError("Jumlah beli harus lebih dari 0.")
        for detail in self.__daftar_detail:
            if detail.get_buku() is buku:
                jumlah_baru = detail.get_jumlah() + jumlah
                if jumlah_baru > buku.get_stok():
                    raise StokTidakCukupError(buku.get_judul(), jumlah_baru, buku.get_stok())
                detail.ubah_jumlah(jumlah_baru)
                self.hitung_total()
                return detail
        if jumlah > buku.get_stok():
            raise StokTidakCukupError(buku.get_judul(), jumlah, buku.get_stok())
        id_detail = f"{self.__id_transaksi}-D{len(self.__daftar_detail) + 1:02d}"
        detail = DetailTransaksi(id_detail, buku, jumlah)
        self.__daftar_detail.append(detail)
        self.hitung_total()
        return detail

    def hitung_total(self):
        self.__total = 0.0
        for detail in self.__daftar_detail:
            self.__total += detail.get_subtotal()
        return self.__total

    # ---- Pembayaran ----
    def hitung_kembalian(self, uang):
        """Mengembalikan kembalian; melempar PembayaranKurangError bila uang kurang."""
        total = self.hitung_total()
        if uang < total:
            raise PembayaranKurangError(total, uang)
        return uang - total

    def proses_pembayaran(self, uang):
        """Validasi pembayaran dan stok, kurangi stok, lalu selesaikan transaksi."""
        self.__pastikan_draft()
        if not self.__daftar_detail:
            raise ValueError("Keranjang masih kosong.")
        kembalian = self.hitung_kembalian(uang)
        # Semua stok dicek dulu sebelum ada yang dikurangi
        for detail in self.__daftar_detail:
            buku = detail.get_buku()
            if detail.get_jumlah() > buku.get_stok():
                raise StokTidakCukupError(buku.get_judul(), detail.get_jumlah(), buku.get_stok())
        for detail in self.__daftar_detail:
            detail.get_buku().kurangi_stok(detail.get_jumlah())
        self.__uang_bayar = uang
        self.__kembalian = kembalian
        self.__status_transaksi = SELESAI
        self.__tanggal_transaksi = datetime.now()
        if self.__pelanggan is not None:
            self.__pelanggan.tambah_riwayat_pembelian(self.ringkasan())
        return kembalian

    def simpan_transaksi(self, penjualan):
        """Menyimpan transaksi yang sudah dibayar ke objek Penjualan."""
        if not self.sudah_selesai():
            raise ValueError("Hanya transaksi yang sudah dibayar yang dapat disimpan.")
        penjualan.simpan_transaksi(self)

    def batalkan_transaksi(self):
        """Membatalkan transaksi Draft. Stok belum berkurang, jadi tidak perlu dikembalikan."""
        self.__pastikan_draft()
        self.__status_transaksi = DIBATALKAN

    # ---- Output ----
    def ringkasan(self):
        return {
            "id_transaksi": self.__id_transaksi,
            "waktu": self.__tanggal_transaksi.strftime("%Y-%m-%d %H:%M:%S"),
            "total": self.__total,
            "item": [
                {"judul": d.get_buku().get_judul(), "jumlah": d.get_jumlah()}
                for d in self.__daftar_detail
            ],
        }

    def cetak_struk(self):
        garis = "=" * 40
        baris = [garis, "        LITERA HOUSE - STRUK", garis,
                 f"No. Transaksi : {self.__id_transaksi}",
                 f"Waktu         : {self.__tanggal_transaksi:%Y-%m-%d %H:%M:%S}",
                 f"Status        : {self.__status_transaksi}"]
        if self.__pelanggan:
            baris.append(f"Pelanggan     : {self.__pelanggan.get_nama()}")
        baris.append("-" * 40)
        for detail in self.__daftar_detail:
            baris.append(detail.tampilkan_detail())
        baris.append("-" * 40)
        baris.append(f"Total   : Rp{self.__total:,.0f}")
        if self.sudah_selesai():
            baris.append(f"Bayar   : Rp{self.__uang_bayar:,.0f}")
            baris.append(f"Kembali : Rp{self.__kembalian:,.0f}")
        baris.append(garis)
        return "\n".join(baris)