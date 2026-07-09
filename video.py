import subprocess
import os

def ffmpeg_ile_kucult(girdi_dosyasi, cikti_dosyasi):
    if os.path.exists(cikti_dosyasi):
        os.remove(cikti_dosyasi)

    # Senin bulduğun FFmpeg exe yolu
    ffmpeg_yolu = r"C:\ffmpeg\bin\ffmpeg.exe"

    video_komut = [
        ffmpeg_yolu,            
        '-i', girdi_dosyasi,
        '-vcodec', 'libx264',   # Sıkıştırma algoritması
        '-crf', '25',           # Kalite faktörü (23 ile 28 arası idealdir)
        '-acodec', 'aac',       # Sesi koruma
        '-b:a', '128k',
        cikti_dosyasi
    ]

    foto_komut = [
        ffmpeg_yolu,
        '-i', girdi_dosyasi,  # Örn: 'resim.jpg'
        '-q:v', '12',              # Fotoğraf kalitesi (1-31 arası. 1 en iyi, 31 en düşük)
        cikti_dosyasi         # Örn: 'yeni_resim.jpg'
    ]
    
    print("FFmpeg çalıştırılıyor, video küçültülüyor... (Bu işlem videonun uzunluğuna göre birkaç dakika sürebilir)")
    # Komutu çalıştır
    subprocess.run(video_komut)
    print("Video başarıyla küçültüldü ve kaydedildi!")

print("Video ve fotoğraf sıkıştırma sitesine hoş geldiniz.")


girdi = r"C:\Users\HSİ\Downloads\Video Project 2.mp4"
cikti = r"C:\Users\HSİ\Downloads\Video Project 2_kucuk_kucuk.mp4"

ffmpeg_ile_kucult(girdi, cikti)

