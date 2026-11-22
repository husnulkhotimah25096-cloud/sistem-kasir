"""Demo CLI sementara. UI Tkinter akan dibuat di langkah berikutnya."""
from buku import BukuFiksi, BukuNonFiksi
from exceptions import LiteraHouseError
from kategori import Kategori
from pelanggan import Pelanggan
from penjualan import Penjualan
from transaksi import Transaksi


def main():
    daftar_kategori, daftar_buku, daftar_pelanggan = [], [], []
    penjualan = Penjualan()

    novel = Kategori("K01", "Novel", "Buku cerita panjang")
    diri = Kategori("K02", "Pengembangan Diri", "Buku pengembangan pribadi")
    novel.tambah_kategori(daftar_kategori)
    diri.tambah_kategori(daftar_kategori)

    laskar = BukuFiksi("B001", "Laskar Pelangi", "Andrea Hirata", 85000, 10, novel, "Drama")
    atomic = BukuNonFiksi("B002", "Atomic Habits", "James Clear", 110000, 5, diri, "Psikologi")
    laskar.tambah_buku(daftar_buku)
    atomic.tambah_buku(daftar_buku)

    Pelanggan("P001", "Budi", "081234567890", "Pekalongan").tambah_pelanggan(daftar_pelanggan)

    for buku in daftar_buku:  # polymorphism
        print(buku.tampilkan_info(), end="\n\n")

    # Fitur Buku: cari, edit, kelola stok, hapus
    print("--- Fitur Buku ---")
    hasil = laskar.cari_buku(daftar_buku, "laskar")
    print("Hasil cari 'laskar':", [b.get_judul() for b in hasil])
    laskar.edit_buku(harga=85000, kategori=novel)
    laskar.tambah_stok(5)
    print("Stok Laskar Pelangi setelah tambah 5:", laskar.get_stok())
    laskar.kurangi_stok(5)
    sementara = BukuFiksi("B999", "Buku Sementara", "Penulis", 10000, 1, novel, "Uji")
    sementara.tambah_buku(daftar_buku)
    sementara.hapus_buku(daftar_buku)
    print("Jumlah buku di daftar:", len(daftar_buku), "\n")

    # 1. Transaksi berhasil
    try:
        trx = Transaksi.buat_transaksi("T001")
        trx.pilih_pelanggan(Pelanggan.cari_pelanggan(daftar_pelanggan, "P001"))
        trx.tambah_detail_transaksi(laskar, 2)
        trx.tambah_detail_transaksi(atomic, 1)

        print("--- Fitur DetailTransaksi ---")
        for detail in trx.get_daftar_detail():
            print(detail.get_id_detail(), "|", detail.tampilkan_detail().replace("\n", " "))
        detail_atomic = trx.get_daftar_detail()[1]
        detail_atomic.ubah_jumlah(2)  # ubah jumlah Atomic Habits dari 1 menjadi 2
        print("Subtotal setelah ubah jumlah:", detail_atomic.get_subtotal(), "\n")

        trx.proses_pembayaran(500000)
        trx.simpan_transaksi(penjualan)
        print(trx.cetak_struk())
    except LiteraHouseError as e:
        print("Error:", e)

    # 2. Pembayaran kurang, lalu dibatalkan
    trx2 = Transaksi.buat_transaksi("T002")
    try:
        trx2.tambah_detail_transaksi(atomic, 2)
        trx2.proses_pembayaran(100000)
    except LiteraHouseError as e:
        print("Error:", e)
        trx2.batalkan_transaksi()
        print("Status T002:", trx2.get_status())

    # 3. Stok tidak cukup
    try:
        Transaksi.buat_transaksi("T003").tambah_detail_transaksi(atomic, 99)
    except LiteraHouseError as e:
        print("Error:", e)

    print(penjualan.cetak_laporan())
    print("Riwayat Budi:", len(daftar_pelanggan[0].lihat_riwayat_pembelian()), "transaksi")


if __name__ == "__main__":
    main()