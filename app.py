import os
import subprocess
import threading
import time
import uuid
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Maksimum dosya boyutu: 1 GB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
ALLOWED_PHOTO_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

# app.py dosyasının bulunduğu ana klasörün tam yolunu otomatik bulur
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Klasörleri bu ana yola göre kesin olarak belirler
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# --- BAŞLANGIÇ TEMİZLİĞİ ---
def baslangic_temizligi():
    print("Sistem baslatiliyor: Klasorler kontrol ediliyor...")
    silinen_dosya_sayisi = 0
    for klasor in [UPLOAD_FOLDER, PROCESSED_FOLDER]:
        for dosya in os.listdir(klasor):
            dosya_yolu = os.path.join(klasor, dosya)
            try:
                if os.path.isfile(dosya_yolu):
                    os.remove(dosya_yolu)
                    silinen_dosya_sayisi += 1
            except Exception as e:
                print(f"Hata: {dosya} silinemedi. Sebep: {e}")
    if silinen_dosya_sayisi > 0:
        print(f"Baslangic temizligi tamamlandi: {silinen_dosya_sayisi} adet eski dosya silindi.\n")
    else:
        print("Klasorler zaten bos, temizlige gerek yok.\n")

# Kodu calistirdigimiz anda temizligi yap
baslangic_temizligi()
# -----------------------------

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

def allowed_file(filename, media_type):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if media_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    elif media_type == 'photo':
        return ext in ALLOWED_PHOTO_EXTENSIONS
    return False

def compress_media(input_path, output_path, media_type):
    if os.path.exists(output_path):
        os.remove(output_path)
    
    if media_type == 'video':
        komut = [
            FFMPEG_PATH,            
            '-i', input_path,
            '-vcodec', 'libx264',
            '-crf', '25',
            '-acodec', 'aac',
            '-b:a', '128k',
            output_path
        ]
    else: 
        komut = [
            FFMPEG_PATH,
            '-i', input_path,
            '-q:v', '12',
            output_path
        ]
    subprocess.run(komut, check=True)

def clean_up_files(path1, path2, delay=600):
    time.sleep(delay)
    print("\nTEMIZLIK ZAMANI: Eski dosyalar siliniyor...")
    try:
        if os.path.exists(path1):
            os.remove(path1)
            print(f"Orijinal dosya silindi: {path1}")
        if os.path.exists(path2):
            os.remove(path2)
            print(f"Sikistirilmis dosya silindi: {path2}")
    except Exception as e:
        print(f"TEMIZLIK HATASI: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print("\n--- YENI DOSYA YUKLEME ISTEGI GELDI ---")
    if 'file' not in request.files:
        return "Dosya bulunamadi!", 400
    
    file = request.files['file']
    media_type = request.form.get('media_type') 
    
    if file.filename == '':
        return "Dosya secilmedi!", 400
        
    if not media_type or media_type not in ['video', 'photo']:
        return "Gecersiz medya turu!", 400

    if file and allowed_file(file.filename, media_type):
        unique_id = str(uuid.uuid4())[:8] 
        safe_filename = secure_filename(file.filename)
        unique_filename = f"{unique_id}_{safe_filename}"
        
        input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        output_filename = f"kucuk_{unique_filename}"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        
        print(f"BILGI: {unique_filename} sunucuya indiriliyor...")
        file.save(input_path)
        print(f"BILGI: Dosya kaydedildi. Sikistirma (FFmpeg) basliyor...")
        
        try:
            compress_media(input_path, output_path, media_type)
            print("BILGI: Sikistirma tamamlandi, kullaniciya indiriliyor!")
            
            threading.Thread(target=clean_up_files, args=(input_path, output_path, 600)).start()
            print("BILGI: Arka plan temizlik sayaci 10 dakika icin baslatildi.\n")

            return send_file(output_path, as_attachment=True)
            
        except Exception as e:
            print(f"FFmpeg HATASI: {str(e)}\n")
            return f"Islem sirasinda hata olustu: {str(e)}", 500
    else:
        return "Guvenlik Uyarisi: Desteklenmeyen dosya uzantisi!", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)