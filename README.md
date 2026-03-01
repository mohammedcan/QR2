# QR Mesaj Uygulaması 📱

Flask tabanlı QR kod mesaj uygulaması. Metin yaz → QR oluştur → tarat → tarayıcıda oku.

## Kurulum

```bash
# 1. Gerekli kütüphaneyi kur (sadece Flask gerekli)
pip install flask

# 2. Uygulamayı çalıştır
python app.py
```

## Kullanım

1. **Tarayıcında aç:** `http://localhost:5000`
2. **Mesaj yaz** ve "QR Oluştur" butonuna bas
3. **QR kodu indir** (PNG olarak) veya linkini kopyala
4. **Telefon ile tarat** → mesaj tarayıcıda açılır ✅

## Aynı Wi-Fi'deki cihazlardan erişim

Uygulama başlarken terminal şunu gösterir:
```
Network: http://192.168.x.x:5000
```
Bu adresi telefonda aç, ya da QR kodu tarat (QR içinde bu adres otomatik gömülür).

## Proje Yapısı

```
qrapp/
├── app.py              # Flask sunucu
├── data.json           # Mesajlar (otomatik oluşur)
├── templates/
│   ├── index.html      # Ana sayfa (QR oluştur)
│   ├── view.html       # Mesaj görüntüleme
│   └── 404.html        # Hata sayfası
└── README.md
```

## Özellikler

- ✅ Her mesaj için benzersiz ID ve QR kodu
- ✅ QR'ı PNG olarak indir
- ✅ Mesajlar `data.json`'da kalıcı saklanır
- ✅ Taratınca tarayıcıda güzel bir sayfa açılır
- ✅ Karanlık tema, mobil uyumlu tasarım
- ✅ Ctrl+Enter kısayolu ile hızlı QR oluştur
