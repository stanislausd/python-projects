# QR Code Decoder

Nihaoo.

Ini kode buatan Dio Rahmat.

Setiap kode yang aku push ke GitHub bakal punya README kayak ini, biar jelas isinya apa, cara pakainya gimana, dan enam bulan lagi waktu aku buka ulang repo ini aku nggak bingung sendiri lihat kode buatan sendiri.

## Kode Ini Ngapain

Script ini baca file gambar QR code, terus mecah isinya. Bukan cuma nampilin teks mentahnya, tapi dia coba kenali dulu itu QR isinya apa: link biasa, teks yang di-encode base64, kartu kontak (vCard), atau kode pembayaran QRIS/EMVCo. Formatnya dicetak duluan, baru isinya.

Ada satu aturan penting: kalau isinya `mailto:` atau `smsto:`, script ini cuma nampilin teksnya di terminal. Nggak bakal buka email client atau ngirim SMS otomatis. Aman dipakai buat cek QR yang nggak jelas asalnya.

## Fungsi di Dalam Kode

- `baca_qr`: buka file gambar dan ambil teks mentah dari QR-nya pakai pyzbar
- `deteksi_format`: nebak QR ini termasuk format apa, dari pola awal teksnya
- `parse_emvco`: bongkar struktur QRIS/EMVCo yang formatnya tag-panjang-nilai, termasuk field yang bersarang
- `parse_vcard`: ambil data kontak dari vCard (nama, telepon, email, dll)
- `is_base64`: cek apakah teksnya valid base64
- `proses`: nentuin cara nampilin hasil sesuai format yang udah terdeteksi

## Yang Perlu Disiapkan

Install dulu library yang dipakai:

```
pip install pyzbar pillow
```

Kalau pakai Linux dan muncul error soal `libzbar`, install juga:

```
sudo apt install libzbar0
```

## Cara Jalanin

1. Taruh file gambar QR code kamu di folder yang sama dengan `qr_decoder.py`.
2. Buka `qr_decoder.py`, cari baris ke-13:

   ```python
   NAMA_FILE_GAMBAR = "qrcode.png"
   ```

   Ganti `"qrcode.png"` sesuai nama file gambar QR kamu.
3. Simpan (Ctrl + S).
4. Jalankan:

   ```
   python qr_decoder.py
   ```

Kalau males edit baris itu, bisa juga langsung kasih nama filenya lewat terminal tanpa ubah kode sama sekali:

```
python qr_decoder.py nama_file_qr.png
```

Hasilnya langsung muncul di terminal, sesuai format QR yang terbaca.

## Kalau Muncul Error `libzbar-64.dll` di Windows

Ini error yang lumayan sering dialami pengguna Windows. Pesannya biasanya `FileNotFoundError: Could not find module 'libzbar-64.dll' (or one of its dependencies)`.

Penyebabnya bukan library-nya gagal diinstall, tapi DLL bawaan pyzbar butuh Visual C++ Redistributable yang belum ada di komputer kamu. Kode di `qr_decoder.py` udah aku tambahin penanganan khusus buat Windows, tapi kalau errornya masih muncul, install dulu:

**Visual C++ Redistributable for Visual Studio 2013 (x64)**, bisa dicari di situs resmi Microsoft, lalu restart terminal atau komputernya.

Kalau sudah diinstall dan masih error juga, coba install ulang pyzbar-nya:

```
pip uninstall pyzbar
pip install pyzbar
```
