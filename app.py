import os
import subprocess
import threading
import time
import uuid
from functools import wraps
from flask import Flask, request, send_file, render_template, session, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# --- GÜVENLİK AYARLARI ---
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
csrf = CSRFProtect(app)

VALID_USERNAME = "Admin"
VALID_PASSWORD_HASH = generate_password_hash('Admin')

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
ALLOWED_PHOTO_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def baslangic_temizligi():
    print("Sistem baslatiliyor: Klasorler kontrol ediliyor...")
    silinen = 0
    for klasor in [UPLOAD_FOLDER, PROCESSED_FOLDER]:
        for dosya in os.listdir(klasor):
            try:
                os.remove(os.path.join(klasor, dosya))
                silinen += 1
            except:
                pass
    if silinen > 0:
        print(f"Baslangic temizligi tamamlandi: {silinen} dosya silindi.\n")

baslangic_temizligi()

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

def format_size(size_in_bytes):
    """Dosya boyutunu okunabilir formata (KB, MB) çevirir."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def compress_media(input_path, output_path, media_type):
    if os.path.exists(output_path):
        os.remove(output_path)
    if media_type == 'video':
        komut = [FFMPEG_PATH, '-i', input_path, '-vcodec', 'libx264', '-crf', '25', '-acodec', 'aac', '-b:a', '128k', output_path]
    else: 
        komut = [FFMPEG_PATH, '-i', input_path, '-q:v', '12', output_path]
    subprocess.run(komut, check=True)

def clean_up_files(path1, path2, delay=300): # İndirme için 15 dakika süre tanıyoruz
    time.sleep(delay)
    try:
        if os.path.exists(path1): os.remove(path1)
        if os.path.exists(path2): os.remove(path2)
    except: pass

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'): return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        if request.form.get('username') == VALID_USERNAME and check_password_hash(VALID_PASSWORD_HASH, request.form.get('password')):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = "Kullanici adi veya sifre hatali!"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Dosya bulunamadi!"}), 400
    
    file = request.files['file']
    media_type = request.form.get('media_type') 
    
    if file.filename == '' or not media_type:
        return jsonify({"error": "Dosya veya tur secilmedi!"}), 400

    if file and allowed_file(file.filename, media_type):
        unique_id = str(uuid.uuid4())[:8] 
        safe_filename = secure_filename(file.filename)
        unique_filename = f"{unique_id}_{safe_filename}"
        
        input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        output_filename = f"kucuk_{unique_filename}"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        
        file.save(input_path)
        
        try:
            # Boyut hesaplama ve sıkıştırma işlemleri
            compress_media(input_path, output_path, media_type)
            
            orijinal_boyut_bayt = os.path.getsize(input_path)
            yeni_boyut_bayt = os.path.getsize(output_path)
            
            # Temizlik sayacını başlat (15 dakika)
            threading.Thread(target=clean_up_files, args=(input_path, output_path, 900)).start()
            
            # Başarı durumunda verileri ön yüze gönder
            return jsonify({
                "status": "success",
                "original_size": format_size(orijinal_boyut_bayt),
                "compressed_size": format_size(yeni_boyut_bayt),
                "filename": output_filename,
                "original_name": file.filename
            })
            
        except Exception as e:
            return jsonify({"error": f"Islem sirasinda hata olustu: {str(e)}"}), 500
    else:
        return jsonify({"error": "Desteklenmeyen dosya uzantisi!"}), 400

# Yeni İndirme Rotası
@app.route('/download/<filename>')
@login_required
def download_file(filename):
    safe_name = secure_filename(filename)
    file_path = os.path.join(PROCESSED_FOLDER, safe_name)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "Dosya bulunamadi veya suresi doldu.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)