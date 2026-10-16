# Titanlar Güvenli SMS Doğrulama (Demo)

Bu Flask projesi SMS bombası değildir. Gerçek SMS göndermeyen bir demo doğrulama akışı içerir.

## Render ayarları
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Environment Variable: `FLASK_SECRET_KEY` için uzun, rastgele bir değer ayarla.

`send_verification_sms()` fonksiyonu bilerek gerçek SMS göndermez. Canlı SMS için kendi SMS sağlayıcı hesabının resmi API'sini kullan; yalnızca açık rıza alınmış numaralara gönderim yap, API anahtarlarını GitHub'a koyma ve sağlayıcı tarafı hız sınırlarını etkinleştir.
