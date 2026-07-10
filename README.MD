🎥 Media Compressor - ArnecaTech
A lightweight web application built with Flask and FFmpeg that allows users to upload, compress, and download media files efficiently. Designed for rapid deployment on local networks or testing environments.

🇬🇧 English
🚀 Features
Easy Compression: Uses FFmpeg to optimize video and photo file sizes.

Async Uploads: Smooth user experience using JavaScript Fetch API.

Security: Basic authentication for access control.

Cleanup: Automatically deletes processed files after 15 minutes.

⚙️ Requirements
Python 3.7+

FFmpeg: Must be installed and configured.

Windows: Ensure it is located at C:\ffmpeg\bin\ffmpeg.exe.

🧪 Installation & Running
Clone the repository and install dependencies:

Bash
pip install -r requirements.txt
Run the application:

Bash
python app.py
Access the application in your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000).

🌐 Expose with ngrok
To test the application over the internet:

Bash
ngrok http 5000
🔐 Login Credentials
Username	Password
Admin	Admin
📁 Project Structure
app.py: Main Flask application.

uploads/: Temporary storage for uploaded files.

processed/: Storage for compressed files.

templates/: HTML interface (index.html, login.html).

static/: Static files (Tailwind CSS, etc.).

📄 License
This project is for educational and testing purposes only.

🇹🇷 Türkçe
🚀 Özellikler
Kolay Sıkıştırma: Video ve fotoğraf dosyalarını FFmpeg ile hızlıca optimize eder.

Asenkron Yükleme: JavaScript Fetch API ile kesintisiz kullanıcı deneyimi.

Güvenlik: Giriş paneli ile temel yetkilendirme.

Otomatik Temizleme: İşlenmiş dosyaları 15 dakika sonra otomatik olarak siler.

⚙️ Gereksinimler
Python 3.7+

FFmpeg: Sisteminizde kurulu ve erişilebilir olmalıdır.

Windows: C:\ffmpeg\bin\ffmpeg.exe yolunda olduğundan emin olun.

🧪 Kurulum ve Çalıştırma
Depoyu klonlayın ve bağımlılıkları yükleyin:

Bash
pip install -r requirements.txt
Uygulamayı çalıştırın:

Bash
python app.py
Tarayıcınızda [http://127.0.0.1:5000](http://127.0.0.1:5000) adresine gidin.

🌐 ngrok ile İnternete Açma
Uygulamayı internet üzerinden test etmek için:

Bash
ngrok http 5000
🔐 Giriş Bilgileri
Kullanıcı Adı	Şifre
Admin	Admin
📁 Proje Yapısı
app.py: Ana Flask uygulaması.

uploads/: Yüklenen dosyaların geçici deposu.

processed/: Sıkıştırılmış dosyaların deposu.

templates/: HTML şablonları (index.html, login.html).

static/: Statik dosyalar (Tailwind CSS vb.).

📄 Lisans
Bu proje eğitim ve test amaçlıdır.