"""Class DetailTransaksi: satu baris item (buku + jumlah) dalam sebuah transaksi."""


class DetailTransaksi:
    def __init__(self, id_detail, buku, jumlah):
        self.__id_detail = id_detail
        self.__buku = buku
        self.__jumlah = 0
        # Harga disimpan saat item dibuat agar perubahan harga buku di kemudian
        # hari tidak mengubah struk transaksi lama.
        self.__harga_satuan = buku.get_harga()
        self.__subtotal = 0.0
        self.__set_jumlah(jumlah)

    def __set_jumlah(self, jumlah):
        if jumlah <= 0:
            raise ValueError("Jumlah beli harus lebih dari 0.")
        self.__jumlah = jumlah
        self.hitung_subtotal()

    # ---- Getter ----
    def get_id_detail(self):
        return self.__id_detail

    def get_buku(self):
        return self.__buku

    def get_jumlah(self):
        return self.__jumlah

    def get_harga_satuan(self):
        return self.__harga_satuan

    def get_subtotal(self):
        return self.__subtotal

    # ---- Operasi ----
    def hitung_subtotal(self):
        self.__subtotal = self.__harga_satuan * self.__jumlah
        return self.__subtotal

    def ubah_jumlah(self, jumlah_baru):
        self.__set_jumlah(jumlah_baru)

    def tampilkan_detail(self):
        """Mengembalikan teks detail item."""
        return (f"{self.__buku.get_judul()}\n"
                f"  {self.__jumlah} x Rp{self.__harga_satuan:,.0f} = Rp{self.__subtotal:,.0f}")