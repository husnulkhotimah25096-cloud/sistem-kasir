# Litera House – Bookstore POS

Sistem kasir toko buku berbasis Python (Pemrograman Berorientasi Objek).

## Menjalankan
```
python main.py            # demo alur kasir
python demo_memori.py     # demonstrasi memory management
python -m unittest discover -s tests -v   # unit test
```

## Struktur
| File | Isi |
|---|---|
| `interfaces.py` | Interface `DapatDitampilkan` |
| `kategori.py` | `Kategori` |
| `buku.py` | `Buku` (abstract), `BukuFiksi`, `BukuNonFiksi` |
| `pelanggan.py` | `Pelanggan` |
| `detail_transaksi.py` | `DetailTransaksi` |
| `transaksi.py` | `Transaksi` |
| `penjualan.py` | `Penjualan` |
| `exceptions.py` | Custom exception |
| `tests/` | Unit test (`unittest`), satu file per class |

## Penerapan tujuh materi PBO
| Materi | Penerapan |
|---|---|
| 1. Class, object, memory management | 8 class utama dan banyak objek; `demo_memori.py` (referensi, reference count, `del`, garbage collector, shallow/deep copy) |
| 2. Encapsulation | Atribut privat `__`, getter/setter dengan validasi, method protected `_info_dasar()` |
| 3. Inheritance | `BukuFiksi` dan `BukuNonFiksi` mewarisi `Buku`; semua exception mewarisi `LiteraHouseError` |
| 4. Polymorphism | `tampilkan_info()` berbeda di tiap class, dipanggil lewat satu loop di `main.py` |
| 5. Abstraction dan interface | `Buku` abstract (`ABC`, `@abstractmethod`); interface `DapatDitampilkan` diimplementasikan `Buku`, `Kategori`, `Pelanggan` |
| 6. Collection dan iterasi | `list` (daftar, keranjang), `dict` (laporan), `tuple` (`STATUS_VALID`, `buku_terlaris`), `set` (`pelanggan_unik`), `for`, `enumerate`, `sorted`, comprehension |
| 7. Exception handling | 6 custom exception, `raise` di semua class, `try/except/else/finally` dan beberapa `except` di `main.py` |
