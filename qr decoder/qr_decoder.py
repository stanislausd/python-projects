import sys
import re
import base64
from PIL import Image
from pyzbar.pyzbar import decode as decode_qr

NAMA_FILE_GAMBAR = "qrcode.png" #ubah disini cuyy

EMVCO_LABELS = {
    "00": "Payload Format Indicator",
    "01": "Point of Initiation Method",
    "52": "Merchant Category Code",
    "53": "Transaction Currency",
    "54": "Transaction Amount",
    "55": "Tip/Convenience Indicator",
    "58": "Country Code",
    "59": "Merchant Name",
    "60": "Merchant City",
    "61": "Postal Code",
    "62": "Additional Data Field",
    "63": "CRC",
    "64": "Merchant Information Language Template",
}


def baca_qr(path_gambar):
    try:
        gambar = Image.open(path_gambar)
    except Exception:
        raise FileNotFoundError(f"Tidak dapat membaca file gambar: {path_gambar}")
    hasil = decode_qr(gambar)
    if not hasil:
        raise ValueError("QR code tidak ditemukan atau tidak dapat dibaca dari gambar")
    return hasil[0].data.decode("utf-8")


def is_base64(teks):
    teks = teks.strip()
    if len(teks) < 8 or len(teks) % 4 != 0:
        return False
    if not re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", teks):
        return False
    try:
        hasil = base64.b64decode(teks, validate=True)
        hasil.decode("utf-8")
        return True
    except Exception:
        return False


def is_tag_nested(tag):
    try:
        angka = int(tag)
    except ValueError:
        return False
    return 26 <= angka <= 51 or angka in (62, 64, 65)


def parse_emvco(data):
    fields = {}
    i = 0
    while i + 4 <= len(data):
        tag = data[i:i + 2]
        panjang_str = data[i + 2:i + 4]
        if not panjang_str.isdigit():
            break
        panjang = int(panjang_str)
        nilai = data[i + 4:i + 4 + panjang]
        fields[tag] = nilai
        i += 4 + panjang
    return fields


def format_emvco(fields, indent=0):
    baris = []
    prefix = "  " * indent
    for tag, nilai in fields.items():
        label = EMVCO_LABELS.get(tag, f"Tag {tag}") if indent == 0 else f"Sub-tag {tag}"
        if is_tag_nested(tag):
            baris.append(f"{prefix}{tag} ({label}):")
            sub_fields = parse_emvco(nilai)
            baris.extend(format_emvco(sub_fields, indent + 1))
        else:
            baris.append(f"{prefix}{tag} ({label}): {nilai}")
    return baris


def parse_vcard(data):
    hasil = {}
    for baris in data.strip().splitlines():
        baris = baris.strip()
        if ":" not in baris:
            continue
        kunci, _, nilai = baris.partition(":")
        kunci = kunci.split(";")[0].upper()
        if kunci in ("BEGIN", "END", "VERSION"):
            continue
        hasil.setdefault(kunci, []).append(nilai)
    return hasil


def deteksi_format(data):
    teks = data.strip()
    if teks.upper().startswith("BEGIN:VCARD"):
        return "vCard"
    if teks.startswith("000201"):
        return "EMVCo"
    if teks.lower().startswith("mailto:"):
        return "mailto"
    if teks.lower().startswith("smsto:") or teks.lower().startswith("sms:"):
        return "smsto"
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", teks):
        return "URL"
    if is_base64(teks):
        return "Base64"
    return "Teks"


def proses(data, fmt):
    if fmt == "URL":
        print(f"URL: {data}")
    elif fmt == "mailto":
        print(f"Alamat email (mailto): {data}")
    elif fmt == "smsto":
        print(f"Nomor tujuan SMS: {data}")
    elif fmt == "Base64":
        hasil = base64.b64decode(data.strip()).decode("utf-8")
        print("Hasil decode Base64:")
        print(hasil)
    elif fmt == "vCard":
        kontak = parse_vcard(data)
        for kunci, daftar_nilai in kontak.items():
            for nilai in daftar_nilai:
                print(f"{kunci}: {nilai}")
    elif fmt == "EMVCo":
        fields = parse_emvco(data)
        for baris in format_emvco(fields):
            print(baris)
    else:
        print("Isi QR:")
        print(data)


def main():
    path_gambar = sys.argv[1] if len(sys.argv) > 1 else NAMA_FILE_GAMBAR
    try:
        data = baca_qr(path_gambar)
    except (FileNotFoundError, ValueError) as e:
        print(str(e))
        sys.exit(1)

    fmt = deteksi_format(data)

    print(f"Format terdeteksi: {fmt}")
    print("-" * 40)
    proses(data, fmt)


if __name__ == "__main__":
    main()
"""Author link: https://github.com/stanislausd"""
