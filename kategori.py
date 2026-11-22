
from exceptions import KategoriTidakDitemukanError


class Kategori:
    def __init__(self, id_kategori, nama_kategori, deskripsi=""):
        self.__id_kategori = id_kategori
        self.__nama_kategori = ""
        self.__deskripsi = ""
        self.set_nama_kategori(nama_kategori)
        self.set_deskripsi(deskripsi)

    # ---- Getter ----
    def get_id_kategori(self):
        return self.__id_kategori

    def get_nama_kategori(self):
        return self.__nama_kategori

    def get_deskripsi(self):
        return self.__deskripsi

    # ---- Setter dengan validasi ----
    def set_nama_kategori(self, nama):
        if not nama.strip():
            raise ValueError("Nama kategori tidak boleh kosong.")
        self.__nama_kategori = nama

    def set_deskripsi(self, deskripsi):
        self.__deskripsi = deskripsi

    # ---- Operasi data kategori ----
    def tambah_kategori(self, daftar_kategori):
        for k in daftar_kategori:
            if k.get_id_kategori() == self.__id_kategori:
                raise ValueError(f"ID kategori '{self.__id_kategori}' sudah terdaftar.")
        daftar_kategori.append(self)

    def edit_kategori(self, nama_baru=None, deskripsi_baru=None):
        if nama_baru is not None:
            self.set_nama_kategori(nama_baru)
        if deskripsi_baru is not None:
            self.set_deskripsi(deskripsi_baru)

    def hapus_kategori(self, daftar_kategori, daftar_buku=None):
        """Menghapus kategori. Bila daftar_buku diberikan, kategori yang
        masih dipakai buku tidak boleh dihapus."""
        if self not in daftar_kategori:
            raise KategoriTidakDitemukanError(self.__id_kategori)
        if daftar_buku is not None:
            for buku in daftar_buku:
                if buku.get_kategori() is self:
                    raise ValueError(
                        f"Kategori '{self.__nama_kategori}' masih dipakai oleh buku "
                        f"'{buku.get_judul()}'."
                    )
        daftar_kategori.remove(self)

    def tampilkan_kategori(self):
        """Mengembalikan teks info kategori."""
        return f"{self.__id_kategori} - {self.__nama_kategori}: {self.__deskripsi}"

    def __str__(self):
        return self.tampilkan_kategori()