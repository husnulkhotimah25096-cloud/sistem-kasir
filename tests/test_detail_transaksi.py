"""Unit test class DetailTransaksi."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from buku import BukuFiksi
from detail_transaksi import DetailTransaksi
from kategori import Kategori


class TestDetailTransaksi(unittest.TestCase):
    def setUp(self):
        kategori = Kategori("K01", "Novel")
        self.buku = BukuFiksi("B001", "Laskar Pelangi", "Andrea", 85000, 10, kategori, "Drama")
        self.detail = DetailTransaksi("T001-D01", self.buku, 2)

    def test_atribut_awal(self):
        self.assertEqual(self.detail.get_id_detail(), "T001-D01")
        self.assertIs(self.detail.get_buku(), self.buku)
        self.assertEqual(self.detail.get_jumlah(), 2)
        self.assertEqual(self.detail.get_harga_satuan(), 85000)

    def test_hitung_subtotal(self):
        self.assertEqual(self.detail.get_subtotal(), 170000)
        self.assertEqual(self.detail.hitung_subtotal(), 170000)

    def test_harga_satuan_tidak_berubah_saat_harga_buku_diubah(self):
        self.buku.set_harga(99000)
        self.assertEqual(self.detail.get_harga_satuan(), 85000)
        self.assertEqual(self.detail.hitung_subtotal(), 170000)

    def test_ubah_jumlah(self):
        self.detail.ubah_jumlah(5)
        self.assertEqual(self.detail.get_jumlah(), 5)
        self.assertEqual(self.detail.get_subtotal(), 425000)

    def test_jumlah_nol_ditolak_saat_dibuat(self):
        with self.assertRaises(ValueError):
            DetailTransaksi("D", self.buku, 0)

    def test_ubah_jumlah_tidak_valid_ditolak(self):
        with self.assertRaises(ValueError):
            self.detail.ubah_jumlah(-1)
        self.assertEqual(self.detail.get_jumlah(), 2)  # tidak berubah

    def test_tampilkan_detail(self):
        teks = self.detail.tampilkan_detail()
        self.assertIn("Laskar Pelangi", teks)
        self.assertIn("2 x", teks)
        self.assertIn("170,000", teks)


if __name__ == "__main__":
    unittest.main()
