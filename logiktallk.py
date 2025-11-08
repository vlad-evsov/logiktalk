import threading
from socket import *
from customtkinter import *
import pygame

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('1080x1080')
        self.label = None
        # menu frame
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -5
        self.btn = CTkButton(self, text='Play', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
        # main
        self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disabled')
        self.chat_field.place(x=0, y=0)
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.place(x=0, y=0)
        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        self.username = 'Влад'
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('192.168.5.120', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        self.adaptive_ui()


        set_appearance_mode("System")
        set_default_color_theme("blue")


        self.music_playing = False
        self.music_file = "img/bc-music.mp3"
        pygame.mixer.init()
        self.music_button = None
        self.music_status_label = None


        self.msg_sound_file = "img/msg-sound.mp3"  # або .mp3
        self.msg_sound = pygame.mixer.Sound(self.msg_sound_file)  # Завантажуємо звук

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='Play')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='Back')
            self.show_menu()
            # setting menu widgets
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame, placeholder_text=self.username)
            self.entry.pack()
            # Theme selection dropdown
            self.theme_label = CTkLabel(self.menu_frame, text='Тема')
            self.theme_label.pack(pady=10)
            self.theme_option = CTkOptionMenu(
                self.menu_frame,
                values=["Темна", "Світла"],
                command=self.change_theme
            )
            self.theme_option.pack(pady=10)

            self.font_label = CTkLabel(self.menu_frame, text='Шрифт')
            self.font_label.pack(pady=10)
            self.font_option = CTkOptionMenu(
                self.menu_frame,
                values=["Arial", "Times New Roman", "Courier New", "Verdana"],
                command=self.change_font
            )
            self.font_option.pack(pady=10)


            self.music_label = CTkLabel(self.menu_frame, text='Музика')
            self.music_label.pack(pady=10)

            self.music_button = CTkButton(
                self.menu_frame,
                text='Play Грати',
                width=140,
                command=self.toggle_music
            )
            self.music_button.pack(pady=5)

            self.music_status_label = CTkLabel(self.menu_frame, text='bc-music', font=('Arial', 10))
            self.music_status_label.pack(pady=2)

    def change_theme(self, theme):
        if theme == "Темна":
            set_appearance_mode("dark")
            set_default_color_theme("dark-blue")
        elif theme == "Світла":
            set_appearance_mode("light")
            set_default_color_theme("blue")

    def change_font(self, font):
        current_font_size = self.chat_field.cget("font")[1]
        self.chat_field.configure(font=(font, 14, 'bold'))

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()
                if hasattr(self, 'theme_label') and self.theme_label:
                    self.theme_label.destroy()
                if hasattr(self, 'theme_option') and self.theme_option:
                    self.theme_option.destroy()
                if hasattr(self, 'font_label') and self.font_label:
                    self.font_label.destroy()
                if hasattr(self, 'font_option') and self.font_option:
                    self.font_option.destroy()
                if hasattr(self, 'music_label') and self.music_label:
                    self.music_label.destroy()
                    self.music_label = None
                if hasattr(self, 'music_button') and self.music_button:
                    self.music_button.destroy()
                    self.music_button = None
                if hasattr(self, 'music_status_label') and self.music_status_label:
                    self.music_status_label.destroy()
                    self.music_status_label = None

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                  height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

        self.after(50, self.adaptive_ui)

    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, 'Я: ' + text + '\n')
        self.chat_field.configure(state='disabled')


        try:
            self.msg_sound.play()
        except:
            pass

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                # Показуємо повідомлення
                self.chat_field.configure(state='normal')
                self.chat_field.insert(END, f"{author}: {message}\n")
                self.chat_field.configure(state='disabled')
                self.chat_field.see(END)


                try:
                    self.msg_sound.play()
                except:
                    pass

        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.chat_field.configure(state='normal')
                self.chat_field.insert(END, f"{author} надіслав(ла) зображення: {filename}\n")
                self.chat_field.configure(state='disabled')
                try:
                    self.msg_sound.play()
                except:
                    pass
        else:
            self.chat_field.configure(state='normal')
            self.chat_field.insert(END, line + "\n")
            self.chat_field.configure(state='disabled')
            try:
                self.msg_sound.play()
            except:
                pass

    def toggle_music(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        if not self.music_playing:
            try:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.play(-1)
                self.music_playing = True
                self.music_button.configure(text='Pause Зупинити')
                self.music_status_label.configure(text='Грає: bc-music')
            except Exception as e:
                self.add_message(f"[ПОМИЛКА МУЗИКИ] {e}")
        else:
            pygame.mixer.music.stop()
            self.music_playing = False
            self.music_button.configure(text='Play Грати')
            self.music_status_label.configure(text='Зупинено')


win = MainWindow()
win.mainloop()