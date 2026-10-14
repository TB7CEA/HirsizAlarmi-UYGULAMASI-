import tkinter as tk
from tkinter import messagebox
import winsound
import threading
import time
import ctypes
import wave
import struct
import math
import os

# =========================================================
# GERÇEK HOPARLÖR İÇİN YÜKSEK SİREN SESİ OLUŞTURUCU (WAV)
# =========================================================
SIREN_DOSYASI = "hirsiz_sireni.wav"

def siren_sesi_olustur():
    """Bilgisayarın gerçek hoparlöründen çalacak yüksek siren dosyası üretir"""
    if os.path.exists(SIREN_DOSYASI):
        return
    
    framerate = 44100
    duration = 3.0  # 3 saniyelik döngüsel siren
    num_samples = int(framerate * duration)
    
    with wave.open(SIREN_DOSYASI, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(framerate)
        
        for i in range(num_samples):
            t = i / framerate
            # Polis Sireni Frekansı (600Hz ile 1800Hz arası dalgalanma)
            freq = 600 + 1200 * (0.5 + 0.5 * math.sin(2 * math.pi * 1.5 * t))
            # MAKSİMUM SES SEVİYESİ (32767 = En Yüksek Ses)
            value = int(32767 * math.sin(2 * math.pi * freq * t))
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

# Siren Dosyasını Oluştur
siren_sesi_olustur()


class HirsizAlarmiPro:
    def __init__(self, root):
        self.root = root
        self.root.title("GÜVENLİK SİSTEMİ - ORÇUN YILMAZ ÇUBUK")
        self.root.geometry("650x550")
        self.root.configure(bg="#0d0d0d")

        self.is_armed = False
        self.alarm_active = False
        self.sifre = "1234" # ALARM SUSTURMA ŞİFRESİ

        self.last_x = 0
        self.last_y = 0

        # Pencere Kapatma Düğmesini Etkisiz Yap
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        # Başlık ve İsim
        self.lbl_owner = tk.Label(
            root, 
            text="ORÇUN YILMAZ ÇUBUK", 
            font=("Arial Black", 26, "bold"), 
            fg="#00ffcc", 
            bg="#0d0d0d"
        )
        self.lbl_owner.pack(pady=20)

        self.lbl_sub = tk.Label(
            root, 
            text="YÜKSEK SESLİ HIRSIZLIK ÖNLEME SİSTEMİ", 
            font=("Helvetica", 12, "bold"), 
            fg="#aaaaaa", 
            bg="#0d0d0d"
        )
        self.lbl_sub.pack(pady=0)

        # Durum Göstergesi
        self.lbl_status = tk.Label(
            root, 
            text="DURUM: SİSTEM HAZIR", 
            font=("Helvetica", 18, "bold"), 
            fg="yellow", 
            bg="#0d0d0d"
        )
        self.lbl_status.pack(pady=40)

        # Alarm Kur Butonu
        self.btn_arm = tk.Button(
            root, 
            text="🚨 ALARMI ETKİNLEŞTİR (5 SN)", 
            font=("Helvetica", 16, "bold"), 
            bg="#ff0000", 
            fg="white", 
            command=self.start_countdown,
            padx=20, 
            pady=15,
            bd=5
        )
        self.btn_arm.pack(pady=10)

        # Şifre Alanı
        self.frame_sifre = tk.Frame(root, bg="#0d0d0d")
        self.entry_sifre = tk.Entry(self.frame_sifre, font=("Helvetica", 20), show="*", justify="center", width=10)
        self.entry_sifre.pack(side=tk.LEFT, padx=10)
        
        self.btn_disarm = tk.Button(
            self.frame_sifre, 
            text="ALARMI SUSTUR", 
            font=("Helvetica", 14, "bold"), 
            bg="#00cc44", 
            fg="white", 
            command=self.disarm_alarm,
            pady=5
        )
        self.btn_disarm.pack(side=tk.LEFT)

    def maximize_windows_volume(self):
        """Windows sesini OTOMATİK %100 yapar"""
        for _ in range(50):
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0) # Sesi yükselt tuşu
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)

    def start_countdown(self):
        self.btn_arm.pack_forget()
        self.frame_sifre.pack(pady=20)
        threading.Thread(target=self.arm_countdown, daemon=True).start()

    def arm_countdown(self):
        for i in range(5, 0, -1):
            self.lbl_status.config(
                text=f"SİSTEM KURULUYOR: {i} SN\nBİLGİSAYARI BIRAKIN VE UZAKLAŞIN!", 
                fg="orange"
            )
            time.sleep(1)
        
        self.is_armed = True
        self.lbl_status.config(
            text="🔒 SİSTEM KİLİTLENDİ!\n(DOKUNULDUĞU AN SİRENLER PATLAYACAK)", 
            fg="#ff3333"
        )
        
        self.last_x = self.root.winfo_pointerx()
        self.last_y = self.root.winfo_pointery()
        
        self.root.bind_all("<Key>", self.trigger_alarm)
        self.root.bind_all("<Button>", self.trigger_alarm)
        self.track_movement()

    def track_movement(self):
        if self.is_armed and not self.alarm_active:
            current_x = self.root.winfo_pointerx()
            current_y = self.root.winfo_pointery()

            if abs(current_x - self.last_x) > 3 or abs(current_y - self.last_y) > 3:
                self.trigger_alarm()
            else:
                self.root.after(50, self.track_movement)

    def trigger_alarm(self, event=None):
        if not self.is_armed or self.alarm_active:
            return
        
        self.alarm_active = True
        self.root.attributes('-fullscreen', True) # Ekranı tamamen kapla
        self.root.attributes('-topmost', True)   # En üstte tut

        # Windows Sesini %100 Yap
        self.maximize_windows_volume()

        # GERÇEK SİREN SESİNİ ÇAL (Döngüsel ve Kesintisiz)
        winsound.PlaySound(SIREN_DOSYASI, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)

        # Çakar Efektini Başlat
        threading.Thread(target=self.flash_screen, daemon=True).start()

    def flash_screen(self):
        # Yüksek Hızlı Çakar Lambası Efekti
        colors = ["#ff0000", "#0055ff", "#ffff00", "#ffffff", "#000000"]
        i = 0
        while self.alarm_active:
            color = colors[i % len(colors)]
            text_color = "black" if color in ["#ffff00", "#ffffff"] else "white"
            
            self.root.configure(bg=color)
            self.lbl_owner.configure(bg=color, fg=text_color)
            self.lbl_sub.configure(bg=color, fg=text_color)
            self.lbl_status.configure(
                text="🚨 HIRSIZ VAR! DOKUNMA! 🚨\nORÇUN YILMAZ ÇUBUK", 
                bg=color, 
                fg=text_color,
                font=("Arial Black", 32, "bold")
            )
            self.frame_sifre.configure(bg=color)
            i += 1
            time.sleep(0.06)

    def disarm_alarm(self):
        girilen_sifre = self.entry_sifre.get()
        if girilen_sifre == self.sifre:
            self.alarm_active = False
            self.is_armed = False
            
            # Sesi Durdur
            winsound.PlaySound(None, 0)
            
            self.root.attributes('-fullscreen', False)
            self.root.attributes('-topmost', False)
            self.root.configure(bg="#0d0d0d")
            
            self.lbl_owner.configure(bg="#0d0d0d", fg="#00ffcc")
            self.lbl_sub.configure(bg="#0d0d0d", fg="#aaaaaa")
            self.lbl_status.configure(
                text="DURUM: SİSTEM DEVRE DIŞI", 
                fg="yellow", 
                bg="#0d0d0d", 
                font=("Helvetica", 18, "bold")
            )
            
            self.frame_sifre.pack_forget()
            self.btn_arm.pack(pady=10)
            self.entry_sifre.delete(0, tk.END)
            
            self.root.unbind_all("<Key>")
            self.root.unbind_all("<Button>")
            
            messagebox.showinfo("BAŞARILI", "Alarm Başarıyla Kapatıldı Orçun Bey.")
        else:
            messagebox.showerror("HATA", "YANLIŞ ŞİFRE!")
            self.entry_sifre.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = HirsizAlarmiPro(root)
    root.mainloop()