
from exceptions import PelangganTidakDitemukanError


class Pelanggan:
    def __init__(self, id_pelanggan, nama, nomor_hp, alamat=""):
        self.__id_pelanggan = id_pelanggan
        self.__nama = ""
        self.__nomor_hp = ""
        self.__alamat = ""
        self.__riwayat_pembelian = []
        self.set_nama(nama)
        self.set_nomor_hp(nomor_hp)
        self.set_alamat(alamat)

    # ---- Getter ----
    def get_id_pelanggan(self):
        return self.__id_pelanggan

    def get_nama(self):
        return self.__nama

    def get_nomor_hp(self):
        return self.__nomor_hp

    def get_alamat(self):
        return self.__alamat

    # ---- Setter dengan validasi ----
    def set_nama(self, nama):
        if not nama.strip():
            raise ValueError("Nama pelanggan tidak boleh kosong.")
        self.__nama = nama

    def set_nomor_hp(self, nomor_hp):
        if not nomor_hp.isdigit():
            raise ValueError("Nomor HP hanya boleh berisi angka.")
        self.__nomor_hp = nomor_hp

    def set_alamat(self, alamat):
        self.__alamat = alamat

    # ---- Operasi data pelanggan ----
    def tambah_pelanggan(self, daftar_pelanggan):
        for p in daftar_pelanggan:
            if p.get_id_pelanggan() == self.__id_pelanggan:
                raise ValueError(f"ID pelanggan '{self.__id_pelanggan}' sudah terdaftar.")
        daftar_pelanggan.append(self)

    def edit_nama_pelanggan(self, nama_baru):
        self.set_nama(nama_baru)

    def edit_nomor_hp(self, nomor_hp_baru):
        self.set_nomor_hp(nomor_hp_baru)

    def edit_alamat(self, alamat_baru):
        self.set_alamat(alamat_baru)

    def hapus_pelanggan(self, daftar_pelanggan):
        if self not in daftar_pelanggan:
            raise PelangganTidakDitemukanError(self.__id_pelanggan)
        daftar_pelanggan.remove(self)

    @staticmethod
    def cari_pelanggan(daftar_pelanggan, id_pelanggan):
        """Mengembalikan pelanggan dengan ID tersebut, atau melempar error."""
        for p in daftar_pelanggan:
            if p.get_id_pelanggan() == id_pelanggan:
                return p
        raise PelangganTidakDitemukanError(id_pelanggan)

    @staticmethod
    def tampilkan_pelanggan(daftar_pelanggan):
        """Mengembalikan list teks, satu entri per pelanggan."""
        return [str(p) for p in daftar_pelanggan]

    def __str__(self):
        return (
            f"ID Pelanggan : {self.__id_pelanggan}\n"
            f"Nama         : {self.__nama}\n"
            f"Nomor HP     : {self.__nomor_hp}\n"
            f"Alamat       : {self.__alamat}"
        )

    # ---- Riwayat pembelian ----
    def tambah_riwayat_pembelian(self, transaksi):
        """Menyimpan ringkasan transaksi ke riwayat pembelian."""
        self.__riwayat_pembelian.append(transaksi)

    def lihat_riwayat_pembelian(self):
        """Mengembalikan salinan list riwayat (list asli tidak bisa diubah dari luar)."""
        return list(self.__riwayat_pembelian)