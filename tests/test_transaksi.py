"""Unit test class Transaksi."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from buku import BukuFiksi, BukuNonFiksi
from exceptions import PembayaranKurangError, StokTidakCukupError
from kategori import Kategori
from pelanggan import Pelanggan
from penjualan import Penjualan
from transaksi import DIBATALKAN, DRAFT, SELESAI, STATUS_VALID, Transaksi


class TestTransaksi(unittest.TestCase):
    def setUp(self):
        kategori = Kategori("K01", "Umum")
        self.laskar = BukuFiksi("B001", "Laskar Pelangi", "Andrea", 85000, 10, kategori, "Drama")
        self.atomic = BukuNonFiksi("B002", "Atomic Habits", "James Clear", 110000, 5,
                                   kategori, "Psikologi")
        self.pelanggan = Pelanggan("P001", "Budi", "0812", "Pekalongan")
        self.trx = Transaksi.buat_transaksi("T001")

    # ---- Pembuatan dan keranjang ----
    def test_transaksi_baru_berstatus_draft(self):
        self.assertEqual(self.trx.get_status(), DRAFT)
        self.assertEqual(self.trx.get_total(), 0)
        self.assertEqual(self.trx.get_daftar_detail(), [])

    def test_pilih_pelanggan(self):
        self.trx.pilih_pelanggan(self.pelanggan)
        self.assertIs(self.trx.get_pelanggan(), self.pelanggan)

    def test_tambah_detail_transaksi(self):
        detail = self.trx.tambah_detail_transaksi(self.laskar, 2)
        self.assertEqual(detail.get_jumlah(), 2)
        self.assertEqual(len(self.trx.get_daftar_detail()), 1)

    def test_buku_sama_digabung(self):
        self.trx.tambah_detail_transaksi(self.laskar, 2)
        self.trx.tambah_detail_transaksi(self.laskar, 3)
        detail = self.trx.get_daftar_detail()
        self.assertEqual(len(detail), 1)
        self.assertEqual(detail[0].get_jumlah(), 5)

    def test_tambah_melebihi_stok_ditolak(self):
        with self.assertRaises(StokTidakCukupError):
            self.trx.tambah_detail_transaksi(self.atomic, 6)
        self.assertEqual(self.trx.get_daftar_detail(), [])

    def test_gabung_melebihi_stok_ditolak(self):
        self.trx.tambah_detail_transaksi(self.atomic, 3)
        with self.assertRaises(StokTidakCukupError):
            self.trx.tambah_detail_transaksi(self.atomic, 3)
        self.assertEqual(self.trx.get_daftar_detail()[0].get_jumlah(), 3)

    def test_jumlah_nol_ditolak(self):
        with self.assertRaises(ValueError):
            self.trx.tambah_detail_transaksi(self.laskar, 0)

    # ---- Total dan kembalian ----
    def test_hitung_total(self):
        self.trx.tambah_detail_transaksi(self.laskar, 2)   # 170.000
        self.trx.tambah_detail_transaksi(self.atomic, 1)   # 110.000
        self.assertEqual(self.trx.hitung_total(), 280000)

    def test_hitung_kembalian(self):
        self.trx.tambah_detail_transaksi(self.laskar, 2)
        self.assertEqual(self.trx.hitung_kembalian(200000), 30000)

    def test_hitung_kembalian_uang_pas(self):
        self.trx.tambah_detail_transaksi(self.laskar, 2)
        self.assertEqual(self.trx.hitung_kembalian(170000), 0)

    def test_hitung_kembalian_uang_kurang(self):
        self.trx.tambah_detail_transaksi(self.laskar, 2)
        with self.assertRaises(PembayaranKurangError) as ctx:
            self.trx.hitung_kembalian(100000)
        self.assertEqual(ctx.exception.total, 170000)

    # ---- Pembayaran ----
    def test_proses_pembayaran_berhasil(self):
        self.trx.tambah_detail_transaksi(self.laskar, 2)
        kembalian = self.trx.proses_pembayaran(200000)
        self.assertEqual(kembalian, 30000)
        self.assertEqual(self.trx.get_status(), SELESAI)
        self.assertEqual(self.trx.get_uang_bayar(), 200000)
        self.assertEqual(self.trx.get_kembalian(), 30000)
        self.assertEqual(self.laskar.get_stok(), 8)  # stok berkurang

    def test_pembayaran_kurang_tidak_mengubah_stok_dan_status(self):
        self.trx.tambah_detail_transaksi(self.laskar, 2)
        with self.assertRaises(PembayaranKurangError):
            self.trx.proses_pembayaran(1000)
        self.assertEqual(self.laskar.get_stok(), 10)
        self.assertEqual(self.trx.get_status(), DRAFT)

    def test_keranjang_kosong_ditolak(self):
        with self.assertRaises(ValueError):
            self.trx.proses_pembayaran(100000)

    def test_stok_divalidasi_ulang_sebelum_dikurangi(self):
        self.trx.tambah_detail_transaksi(self.laskar, 2)
        self.trx.tambah_detail_transaksi(self.atomic, 3)
        self.atomic.kurangi_stok(4)  # stok Atomic Habits tinggal 1, kurang dari keranjang
        with self.assertRaises(StokTidakCukupError):
            self.trx.proses_pembayaran(10000000)
        self.assertEqual(self.laskar.get_stok(), 10)  # tidak ada yang dikurangi
        self.assertEqual(self.trx.get_status(), DRAFT)

    def test_riwayat_pelanggan_tersimpan_setelah_bayar(self):
        self.trx.pilih_pelanggan(self.pelanggan)
        self.trx.tambah_detail_transaksi(self.laskar, 1)
        self.trx.proses_pembayaran(100000)
        riwayat = self.pelanggan.lihat_riwayat_pembelian()
        self.assertEqual(len(riwayat), 1)
        self.assertEqual(riwayat[0]["id_transaksi"], "T001")

    def test_transaksi_selesai_tidak_bisa_diubah(self):
        self.trx.tambah_detail_transaksi(self.laskar, 1)
        self.trx.proses_pembayaran(100000)
        with self.assertRaises(ValueError):
            self.trx.tambah_detail_transaksi(self.laskar, 1)
        with self.assertRaises(ValueError):
            self.trx.proses_pembayaran(100000)

    # ---- Batal dan simpan ----
    def test_batalkan_transaksi(self):
        self.trx.tambah_detail_transaksi(self.laskar, 2)
        self.trx.batalkan_transaksi()
        self.assertEqual(self.trx.get_status(), DIBATALKAN)
        self.assertEqual(self.laskar.get_stok(), 10)

    def test_transaksi_dibatalkan_tidak_bisa_dibayar(self):
        self.trx.tambah_detail_transaksi(self.laskar, 1)
        self.trx.batalkan_transaksi()
        with self.assertRaises(ValueError):
            self.trx.proses_pembayaran(100000)

    def test_simpan_transaksi_ke_penjualan(self):
        penjualan = Penjualan()
        self.trx.tambah_detail_transaksi(self.laskar, 1)
        self.trx.proses_pembayaran(100000)
        self.trx.simpan_transaksi(penjualan)
        self.assertEqual(penjualan.hitung_jumlah_transaksi(), 1)

    def test_simpan_transaksi_belum_dibayar_ditolak(self):
        self.trx.tambah_detail_transaksi(self.laskar, 1)
        with self.assertRaises(ValueError):
            self.trx.simpan_transaksi(Penjualan())

    # ---- Struk ----
    def test_cetak_struk(self):
        self.trx.pilih_pelanggan(self.pelanggan)
        self.trx.tambah_detail_transaksi(self.laskar, 2)
        self.trx.proses_pembayaran(200000)
        struk = self.trx.cetak_struk()
        for teks in ("LITERA HOUSE", "T001", "Budi", "Laskar Pelangi",
                     "170,000", "200,000", "30,000"):
            self.assertIn(teks, struk)


class TestUbahDanHapusItem(unittest.TestCase):
    def setUp(self):
        kategori = Kategori("K01", "Umum")
        self.laskar = BukuFiksi("B001", "Laskar Pelangi", "Andrea", 85000, 10, kategori, "Drama")
        self.atomic = BukuNonFiksi("B002", "Atomic Habits", "James Clear", 110000, 5,
                                   kategori, "Psikologi")
        self.trx = Transaksi.buat_transaksi("T001")
        self.trx.tambah_detail_transaksi(self.laskar, 2)
        self.trx.tambah_detail_transaksi(self.atomic, 1)

    def test_ubah_jumlah_detail(self):
        self.trx.ubah_jumlah_detail(self.laskar, 4)
        self.assertEqual(self.trx.get_daftar_detail()[0].get_jumlah(), 4)
        self.assertEqual(self.trx.get_total(), 4 * 85000 + 110000)

    def test_ubah_jumlah_detail_melebihi_stok_ditolak(self):
        with self.assertRaises(StokTidakCukupError):
            self.trx.ubah_jumlah_detail(self.atomic, 6)
        self.assertEqual(self.trx.get_daftar_detail()[1].get_jumlah(), 1)

    def test_ubah_jumlah_detail_nol_ditolak(self):
        with self.assertRaises(ValueError):
            self.trx.ubah_jumlah_detail(self.laskar, 0)

    def test_ubah_jumlah_buku_yang_tidak_di_keranjang_ditolak(self):
        asing = BukuFiksi("B9", "Asing", "P", 1000, 5, Kategori("K9", "X"), "g")
        with self.assertRaises(ValueError):
            self.trx.ubah_jumlah_detail(asing, 1)

    def test_hapus_detail_transaksi(self):
        self.trx.hapus_detail_transaksi(self.laskar)
        detail = self.trx.get_daftar_detail()
        self.assertEqual(len(detail), 1)
        self.assertIs(detail[0].get_buku(), self.atomic)
        self.assertEqual(self.trx.get_total(), 110000)

    def test_hapus_buku_yang_tidak_di_keranjang_ditolak(self):
        self.trx.hapus_detail_transaksi(self.laskar)
        with self.assertRaises(ValueError):
            self.trx.hapus_detail_transaksi(self.laskar)

    def test_id_detail_tidak_kembar_setelah_hapus(self):
        self.trx.hapus_detail_transaksi(self.laskar)          # sisa D02
        baru = BukuFiksi("B3", "Baru", "P", 1000, 5, Kategori("K3", "Y"), "g")
        self.trx.tambah_detail_transaksi(baru, 1)              # harus D03, bukan D02
        ids = [d.get_id_detail() for d in self.trx.get_daftar_detail()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_tidak_bisa_diubah_setelah_selesai(self):
        self.trx.proses_pembayaran(10000000)
        with self.assertRaises(ValueError):
            self.trx.ubah_jumlah_detail(self.laskar, 1)
        with self.assertRaises(ValueError):
            self.trx.hapus_detail_transaksi(self.laskar)


class TestStatusTransaksi(unittest.TestCase):
    def test_status_valid_adalah_tuple(self):
        self.assertIsInstance(STATUS_VALID, tuple)
        self.assertEqual(STATUS_VALID, (DRAFT, SELESAI, DIBATALKAN))

    def test_status_transaksi_selalu_termasuk_status_valid(self):
        kategori = Kategori("K01", "Umum")
        buku = BukuFiksi("B1", "J", "P", 1000, 5, kategori, "g")
        trx = Transaksi.buat_transaksi("T1")
        self.assertIn(trx.get_status(), STATUS_VALID)
        trx.tambah_detail_transaksi(buku, 1)
        trx.proses_pembayaran(1000)
        self.assertIn(trx.get_status(), STATUS_VALID)


if __name__ == "__main__":
    unittest.main()
