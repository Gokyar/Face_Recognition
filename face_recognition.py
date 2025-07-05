import tkinter as tk
from tkinter import messagebox
import cv2
import os
import numpy as np
import face_recognition
import pickle
from PIL import Image, ImageTk


# Giriş bilgileri
ADMIN_KULLANICI = "admin"
ADMIN_SIFRE = "1234"

# Embedding'i kaydet

def embedding_kaydet(name, image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        embedding = encodings[0]
        os.makedirs("embeddings", exist_ok=True)
        with open(f"embeddings/{name}.pkl", "wb") as f:
            pickle.dump((name, embedding), f)

# Fotoğraf çekme ve kaydetme işlemi

def foto_cek(name, stage, adim_label, devam_button, image_count, adim_sira):
    folder_path = f"faces/{name}"
    os.makedirs(folder_path, exist_ok=True)

    video_capture = cv2.VideoCapture(0)

    while image_count < 10:
        ret, frame = video_capture.read()
        if not ret:
            break
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)

        for face_location in face_locations:
            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            face_image = frame[top:bottom, left:right]
            image_path = os.path.join(folder_path, f"{name}_{stage}_{image_count}.jpg")
            cv2.imwrite(image_path, face_image)
            image_count += 1
            if stage == 1 and image_count == 1:
                embedding_kaydet(name, image_path)

        cv2.imshow('Kamera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    adim_label.config(text=f"{name} için {adim_sira} aşama tamamlandı!")
    devam_button.config(state=tk.NORMAL)

# Fotoğraf çekme işlemi

def veri_toplama_penceresi(name):
    veri_pencere = tk.Toplevel(pencere)
    veri_pencere.title("Yüz Verisi Toplama")
    veri_pencere.geometry("400x300")

    adim_label = tk.Label(veri_pencere, text="Lütfen yüzünüzü düz tutun", font=("Helvetica", 12))
    adim_label.pack(pady=20)

    devam_button = tk.Button(veri_pencere, text="Devam", width=20, height=2, bg="#4caf50", fg="white")
    devam_button.pack(pady=20)

    image_count = 0
    adim_sayaci = tk.IntVar(value=1)

    def adim_gecis():
        nonlocal image_count
        adim_sira = adim_sayaci.get()
        if adim_sira == 1:
            adim_label.config(text="Lütfen yüzünüzü düz tutun.")
            foto_cek(name, 1, adim_label, devam_button, image_count, "Düz tutma")
            adim_sayaci.set(2)
            adim_label.config(text="Şimdi sağa dönün ve 'Devam' butonuna tıklayın.")
        elif adim_sira == 2:
            adim_label.config(text="Lütfen hafif sağa dönün.")
            foto_cek(name, 2, adim_label, devam_button, image_count, "Sağa dönme")
            adim_sayaci.set(3)
            adim_label.config(text="Şimdi sola dönün ve 'Devam' butonuna tıklayın.")
        elif adim_sira == 3:
            adim_label.config(text="Lütfen biraz daha sola dönün.")
            foto_cek(name, 3, adim_label, devam_button, image_count, "Sola daha fazla dönme")
            adim_sayaci.set(4)
            adim_label.config(text="Şimdi başınızı yukarı kaldırın ve 'Devam' butonuna tıklayın.")
        elif adim_sira == 4:
            adim_label.config(text="Lütfen başınızı hafif yukarı kaldırın.")
            foto_cek(name, 4, adim_label, devam_button, image_count, "Yukarı kaldırma")
            adim_label.config(text="Tüm fotoğraflar çekildi!")
            devam_button.config(state=tk.DISABLED)
            veri_pencere.after(2000, veri_pencere.destroy)

    devam_button.config(command=adim_gecis)

# Yeni yüz eklemeden önce admin girişi

def admin_giris():
    giris_pencere = tk.Toplevel(pencere)
    giris_pencere.title("Admin Girişi")
    giris_pencere.geometry("300x200")

    tk.Label(giris_pencere, text="Kullanıcı Adı:").pack(pady=5)
    kullanici_entry = tk.Entry(giris_pencere)
    kullanici_entry.pack(pady=5)

    tk.Label(giris_pencere, text="Şifre:").pack(pady=5)
    sifre_entry = tk.Entry(giris_pencere, show="*")
    sifre_entry.pack(pady=5)

    def dogrula():
        if kullanici_entry.get() == ADMIN_KULLANICI and sifre_entry.get() == ADMIN_SIFRE:
            giris_pencere.destroy()
            yeni_yuz_ekle()
        else:
            messagebox.showerror("Hata", "Geçersiz kullanıcı adı veya şifre!")

    tk.Button(giris_pencere, text="Giriş Yap", command=dogrula, width=15, bg="#4caf50", fg="white").pack(pady=20)

# Ad girişini soracak pencere

def yeni_yuz_ekle():
    ad_window = tk.Toplevel(pencere)
    ad_window.title("Kişi Adı")
    ad_window.geometry("300x150")

    label = tk.Label(ad_window, text="Kişi Adını Girin:", font=("Helvetica", 12))
    label.pack(pady=10)

    ad_entry = tk.Entry(ad_window, width=25)
    ad_entry.pack(pady=5)

    def devam():
        name = ad_entry.get()
        if not name:
            messagebox.showwarning("Uyarı", "Lütfen isim girin.")
            return
        if os.path.exists(f"faces/{name}"):
            messagebox.showerror("Hata", f"{name} zaten kayıtlı!")
            return
        ad_window.destroy()
        veri_toplama_penceresi(name)

    devam_button = tk.Button(ad_window, text="Devam", command=devam, width=20, height=2, bg="#4caf50", fg="white")
    devam_button.pack(pady=20)

# Embedding'lerden tanıma
def kamera_dogrulama_penceresi():
    dogrulama_pencere = tk.Toplevel(pencere)
    dogrulama_pencere.title("Kamera ile Doğrulama")
    dogrulama_pencere.geometry("600x500")

    mesaj_label = tk.Label(dogrulama_pencere, text="Lütfen kameraya bakınız", font=("Helvetica", 14))
    mesaj_label.pack(pady=10)

    giris_button = tk.Button(dogrulama_pencere, text="Giriş Yap", state=tk.DISABLED, width=20, height=2, bg="#4caf50", fg="white")
    giris_button.pack(pady=10)

    video_label = tk.Label(dogrulama_pencere)
    video_label.pack()

    embedding_list = []
    for filename in os.listdir("embeddings"):
        if filename.endswith(".pkl"):
            with open(os.path.join("embeddings", filename), "rb") as f:
                name, embedding = pickle.load(f)
                embedding_list.append((name, embedding))

    isimler = [isim for isim, emb in embedding_list]
    veriler = [emb for isim, emb in embedding_list]

    cap = cv2.VideoCapture(0)
    recognized_name = [None]

    def video_akisi():
        ret, frame = cap.read()
        if not ret:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        yuz_konumlari = face_recognition.face_locations(rgb)
        yuz_embeddingleri = face_recognition.face_encodings(rgb, yuz_konumlari)

        for (y1, x2, y2, x1), test_embedding in zip(yuz_konumlari, yuz_embeddingleri):
            mesafeler = face_recognition.face_distance(veriler, test_embedding)
            min_index = np.argmin(mesafeler)
            if mesafeler[min_index] < 0.45:
                isim = isimler[min_index]
                mesaj_label.config(text=f"Hoşgeldin {isim}!")
                giris_button.config(state=tk.NORMAL)
                recognized_name[0] = isim
                break

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img.resize((500, 350)))
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        if not recognized_name[0]:s
            dogrulama_pencere.after(100, video_akisi)

    def giris_yapildi():
        messagebox.showinfo("Giriş Başarılı", f"Giriş yapıldı: {recognized_name[0]}")
        cap.release()
        dogrulama_pencere.destroy()

    giris_button.config(command=giris_yapildi)
    video_akisi()

# Çıkış fonksiyonu
def cikis():
    pencere.destroy()

# Ana Arayüz
pencere = tk.Tk()
pencere.title("Yüz Doğrulama Sistemi")
pencere.geometry("400x400")
pencere.configure(bg="#2e2e2e")

tk.Label(pencere, text="Yüz Doğrulama Arayüzü", fg="white", bg="#2e2e2e", font=("Helvetica", 14, "bold")).pack(pady=20)

tk.Button(pencere, text="Yeni Yüz Ekle", command=admin_giris, width=25, height=2, bg="#4caf50", fg="white").pack(pady=5)
tk.Button(pencere, text="Yüz Doğrula", command=kamera_dogrulama_penceresi, width=25, height=2, bg="#2196f3", fg="white").pack(pady=5)
tk.Button(pencere, text="Çıkış", command=cikis, width=25, height=2, bg="#f44336", fg="white").pack(pady=5)

pencere.mainloop()
