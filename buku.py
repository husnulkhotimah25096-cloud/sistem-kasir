"""Class Buku (abstract) dan turunannya. Versi perbaikan dari kode asli.

Perubahan utama:
- Atribut privat + getter/setter dengan validasi (encapsulation)
- Buku menjadi abstract class; BukuFiksi dan BukuNonFiksi mewarisinya
- Method mengembalikan nilai / melempar exception, tidak lagi print
"""
from abc import abstractmethod

from exceptions import BukuTidakDitemukanError, StokTidakCukupError
from interfaces import DapatDitampilkan


class Buku(DapatDitampilkan):
    def __init__(self, kode_buku, judul, penulis, harga, stok, kategori):
        self.__kode_buku = kode_buku
        self.__judul = ""
        self.__penulis = ""
        self.__harga = 0.0
        self.__stok = 0
        self.__kategori = None
        self.set_judul(judul)
        self.set_penulis(penulis)
        self.set_harga(harga)
        self.set_stok(stok)
        self.set_kategori(kategori)

    # ---- Getter ----
    def get_kode_buku(self):
        return self.__kode_buku

    def get_judul(self):
        return self.__judul

    def get_penulis(self):
        return self.__penulis

    def get_harga(self):
        return self.__harga

    def get_stok(self):
        return self.__stok

    def get_kategori(self):
        return self.__kategori

    # ---- Setter dengan validasi ----
    def set_judul(self, judul):
        if not judul.strip():
            raise ValueError("Judul tidak boleh kosong.")
        self.__judul = judul

    def set_penulis(self, penulis):
        if not penulis.strip():
            raise ValueError("Penulis tidak boleh kosong.")
        self.__penulis = penulis

    def set_harga(self, harga):
        if harga < 0:
            raise ValueError("Harga tidak boleh negatif.")
        self.__harga = float(harga)

    def set_stok(self, stok):
        if stok < 0:
            raise ValueError("Stok tidak boleh negatif.")
        self.__stok = int(stok)

    def set_kategori(self, kategori):
        # Objek Kategori; tidak boleh None
        if kategori is None:
            raise ValueError("Kategori tidak boleh kosong.")
        self.__kategori = kategori

    # ---- Operasi data buku ----
    def tambah_buku(self, daftar_buku):
        for b in daftar_buku:
            if b.get_kode_buku() == self.__kode_buku:
                raise ValueError(f"Kode buku '{self.__kode_buku}' sudah terdaftar.")
        daftar_buku.append(self)

    def edit_buku(self, judul=None, penulis=None, harga=None, stok=None, kategori=None):
        if judul is not None:
            self.set_judul(judul)
        if penulis is not None:
            self.set_penulis(penulis)
        if harga is not None:
            self.set_harga(harga)
        if stok is not None:
            self.set_stok(stok)
        if kategori is not None:
            self.set_kategori(kategori)

    def hapus_buku(self, daftar_buku):
        if self not in daftar_buku:
            raise BukuTidakDitemukanError(self.__kode_buku)
        daftar_buku.remove(self)

    @staticmethod
    def cari_buku(daftar_buku, kata_kunci):
        """Mengembalikan list buku yang judul atau kodenya memuat kata kunci."""
        kunci = kata_kunci.strip().lower()
        hasil = []
        for buku in daftar_buku:
            if kunci in buku.get_judul().lower() or kunci in buku.get_kode_buku().lower():
                hasil.append(buku)
        return hasil

    # ---- Stok ----
    def tambah_stok(self, jumlah):
        if jumlah <= 0:
            raise ValueError("Jumlah harus lebih dari 0.")
        self.__stok += jumlah

    def kurangi_stok(self, jumlah):
        if jumlah <= 0:
            raise ValueError("Jumlah harus lebih dari 0.")
        if jumlah > self.__stok:
            raise StokTidakCukupError(self.__judul, jumlah, self.__stok)
        self.__stok -= jumlah

    # ---- Tampilan (polymorphism) ----
    @abstractmethod
    def tampilkan_info(self):
        """Mengembalikan teks info buku; berbeda untuk tiap jenis buku."""

    def _info_dasar(self):
        return (
            f"Kode Buku : {self.__kode_buku}\n"
            f"Judul     : {self.__judul}\n"
            f"Penulis   : {self.__penulis}\n"
            f"Harga     : Rp{self.__harga:,.0f}\n"
            f"Stok      : {self.__stok}\n"
            f"Kategori  : {self.__kategori.get_nama_kategori()}"
        )


class BukuFiksi(Buku):
    def __init__(self, kode_buku, judul, penulis, harga, stok, kategori, genre):
        super().__init__(kode_buku, judul, penulis, harga, stok, kategori)
        self.__genre = genre

    def get_genre(self):
        return self.__genre

    def tampilkan_info(self):
        return f"{self._info_dasar()}\nJenis     : Fiksi (genre: {self.__genre})"


class BukuNonFiksi(Buku):
    def __init__(self, kode_buku, judul, penulis, harga, stok, kategori, bidang):
        super().__init__(kode_buku, judul, penulis, harga, stok, kategori)
        self.__bidang = bidang

    def get_bidang(self):
        return self.__bidang

    def tampilkan_info(self):
        return f"{self._info_dasar()}\nJenis     : Non-Fiksi (bidang: {self.__bidang})"
