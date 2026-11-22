"""Custom exception untuk aplikasi Litera House."""


class LiteraHouseError(Exception):
    """Exception dasar untuk semua kesalahan di aplikasi Litera House."""


class StokTidakCukupError(LiteraHouseError):
    """Dilempar ketika jumlah buku yang dibeli melebihi stok."""

    def __init__(self, judul, diminta, tersedia):
        self.judul = judul
        self.diminta = diminta
        self.tersedia = tersedia
        super().__init__(
            f"Stok '{judul}' tidak cukup: diminta {diminta}, tersedia {tersedia}."
        )


class PelangganTidakDitemukanError(LiteraHouseError):
    """Dilempar ketika data pelanggan tidak ditemukan."""

    def __init__(self, id_pelanggan):
        self.id_pelanggan = id_pelanggan
        super().__init__(f"Pelanggan dengan ID '{id_pelanggan}' tidak ditemukan.")


class PembayaranKurangError(LiteraHouseError):
    """Dilempar ketika uang pembayaran kurang dari total belanja."""

    def __init__(self, total, dibayar):
        self.total = total
        self.dibayar = dibayar
        super().__init__(
            f"Pembayaran kurang: total Rp{total:,.0f}, dibayar Rp{dibayar:,.0f}."
        )


class BukuTidakDitemukanError(LiteraHouseError):
    """Dilempar ketika data buku tidak ditemukan."""

    def __init__(self, kode_buku):
        self.kode_buku = kode_buku
        super().__init__(f"Buku dengan kode '{kode_buku}' tidak ditemukan.")


class KategoriTidakDitemukanError(LiteraHouseError):
    """Dilempar ketika data kategori tidak ditemukan."""

    def __init__(self, id_kategori):
        self.id_kategori = id_kategori
        super().__init__(f"Kategori dengan ID '{id_kategori}' tidak ditemukan.")