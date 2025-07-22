import tkinter as tk
import pygame

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("計時器")
        self.root.configure(bg="#d3d3d3")  # 稍微灰的背景
        self.root.resizable(False, False)  # 禁用調整大小
        self.root.attributes("-topmost", True)  # 總是在最上層

        self.time_var = tk.StringVar(value="00:00:00")
        self.is_running = False
        self.seconds = 0
        self.last_hour_sound_played = False

        self.label = tk.Label(root, textvariable=self.time_var, font=("Arial", 48), bg="#d3d3d3", fg="#333")
        self.label.pack(padx=(10,10),pady=(0, 0))  # 調整上方和下方的間距

        self.start_button = tk.Button(root, text="開始", command=self.toggle_timer, font=("Arial", 24), bg="#333", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=20, pady=(0, 10))  # 調整按鈕的下方間距

        self.reset_button = tk.Button(root, text="重置", command=self.reset_timer, font=("Arial", 24), bg="#333", fg="white")
        self.reset_button.pack(side=tk.RIGHT, padx=20, pady=(0, 10))  # 調整按鈕的下方間距


        self.update_timer()

        # 初始化 pygame
        pygame.mixer.init()
        self.sound_mp3 = pygame.mixer.Sound("sound.mp3")  # 加載每30秒播放的音效
        self.sound_wav = pygame.mixer.Sound("sound.wav")  # 加載每小時播放的音效

        # 設置音量
        self.sound_mp3.set_volume(0.5)  # 設置每30秒音效的音量為50%
        self.sound_wav.set_volume(0.5)   # 設置每小時音效的音量為80%

    def toggle_timer(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.start_button.config(text="暫停")
        else:
            self.start_button.config(text="開始")

    def reset_timer(self):
        self.is_running = False
        self.seconds = 0
        self.time_var.set("00:00:00")
        self.start_button.config(text="開始")

    def update_timer(self):
        if self.is_running:
            self.seconds += 1
            hours, remainder = divmod(self.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_var.set(f"{hours:02}:{minutes:02}:{seconds:02}")

            # 每30秒響鈴一次
            if self.seconds % 30 == 0 and self.seconds % 600 != 0:
                self.sound_mp3.play()  # 播放每30秒的音效

            # 每小時播放 sound.wav
            if self.seconds % 600 == 0:
                self.sound_mp3.play()  # 播放10分鐘的音效



        self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()