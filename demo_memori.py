"""Demonstrasi memory management di Python memakai objek proyek Litera House.

Jalankan: python demo_memori.py
Topik: referensi vs objek, reference count, del, garbage collector,
       shallow copy vs deep copy.
"""
import copy
import gc
import sys
import weakref

from buku import BukuFiksi
from kategori import Kategori
from pelanggan import Pelanggan
from transaksi import Transaksi


def judul(teks):
    print(f"\n=== {teks} ===")


def jumlah_referensi(objek):
    # getrefcount menambah 1 referensi sementara (argumennya sendiri), jadi dikurangi 1
    return sys.getrefcount(objek) - 1


kategori = Kategori("K01", "Novel")

# 1. Variabel adalah referensi (label), bukan wadah nilai
judul("1. Referensi vs objek")
a = BukuFiksi("B001", "Laskar Pelangi", "Andrea", 85000, 10, kategori, "Drama")
b = a                                                                  # b menunjuk objek YANG SAMA
c = BukuFiksi("B001", "Laskar Pelangi", "Andrea", 85000, 10, kategori, "Drama")  # objek baru
print("id(a) == id(b) :", id(a) == id(b), "-> a dan b satu objek")
print("a is b         :", a is b)
print("a is c         :", a is c, "-> c objek lain walau isinya sama")
b.tambah_stok(5)
print("Stok a setelah b.tambah_stok(5):", a.get_stok(), "(berubah, karena a dan b satu objek)")
print("Stok c tidak ikut berubah       :", c.get_stok())

# 2. Reference count dan del
judul("2. Reference count dan del")
x = BukuFiksi("B002", "Dilan", "Pidi Baiq", 70000, 3, kategori, "Roman")
print("Jumlah referensi ke x      :", jumlah_referensi(x))
y = x
print("Setelah y = x              :", jumlah_referensi(x))
del y
print("Setelah del y              :", jumlah_referensi(x), "(objek tetap hidup)")

# 3. Objek dibebaskan saat referensi terakhir hilang
judul("3. Objek dibebaskan otomatis")
sementara = BukuFiksi("B003", "Sementara", "Penulis", 1000, 1, kategori, "Uji")
pantau = weakref.ref(sementara)  # weakref tidak menambah reference count
print("Objek masih ada?     :", pantau() is not None)
del sementara
print("Setelah del, ada?    :", pantau() is not None, "(refcount 0 -> memori dibebaskan)")

# 4. Garbage collector menangani referensi melingkar
judul("4. Garbage collector dan referensi melingkar")


class Simpul:
    def __init__(self):
        self.pasangan = None


s1, s2 = Simpul(), Simpul()
s1.pasangan, s2.pasangan = s2, s1   # saling menunjuk -> refcount tidak pernah 0
pantau_s1 = weakref.ref(s1)
del s1, s2
print("Setelah del, masih ada?:", pantau_s1() is not None, "(terjebak karena saling menunjuk)")
dibersihkan = gc.collect()
print("Setelah gc.collect()   :", pantau_s1() is not None, f"(objek dibersihkan: {dibersihkan})")

# 5. Transaksi menyimpan REFERENSI ke buku, tetapi harga disimpan sebagai SALINAN nilai
judul("5. Referensi di dalam Transaksi")
trx = Transaksi.buat_transaksi("T001")
detail = trx.tambah_detail_transaksi(a, 1)
print("detail.get_buku() is a :", detail.get_buku() is a, "(referensi ke objek yang sama)")
a.set_harga(99000)
print("Harga buku sekarang    :", a.get_harga())
print("Harga di detail        :", detail.get_harga_satuan(), "(angka disalin saat item dibuat)")

# 6. Shallow copy vs deep copy
judul("6. Shallow copy vs deep copy")
riwayat = [{"id_transaksi": "T001", "total": 85000}]

dangkal = copy.copy(riwayat)        # list baru, tetapi dict di dalamnya DIPAKAI BERSAMA
dangkal.append({"id_transaksi": "T002", "total": 1})
print("Shallow copy, tambah item -> riwayat asli:", len(riwayat), "item (aman)")
dangkal[0]["total"] = 0
print("Shallow copy, ubah isi dict -> total asli :", riwayat[0]["total"], "(ikut berubah!)")

riwayat[0]["total"] = 85000
dalam = copy.deepcopy(riwayat)      # semua level disalin
dalam[0]["total"] = 0
print("Deep copy, ubah isi dict    -> total asli :", riwayat[0]["total"], "(aman)")

# Pelanggan memakai deep copy untuk melindungi riwayatnya (encapsulation)
pelanggan = Pelanggan("P001", "Budi", "0812")
pelanggan.tambah_riwayat_pembelian({"id_transaksi": "T001", "total": 85000})
pelanggan.lihat_riwayat_pembelian()[0]["total"] = 0
print("Ubah hasil lihat_riwayat_pembelian() -> total asli:",
      pelanggan.lihat_riwayat_pembelian()[0]["total"], "(aman karena deep copy)")
