import os
import threading
import tkinter as tk
import webbrowser
import customtkinter as ctk
from yt_dlp import YoutubeDL

# Настройка темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class YouTubeDownloader(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("YouTube MP3 / MP4 Downloader")
        self.geometry("580x500")
        self.resizable(False, False)

        # Путь сохранения по умолчанию
        self.save_directory = os.getcwd()

        # Главный контейнер
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Заголовок
        self.label_title = ctk.CTkLabel(
            self.main_frame,
            text="Загрузчик с YouTube",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.label_title.pack(pady=(20, 15))

        # Поле ввода URL
        self.entry_url = ctk.CTkEntry(
            self.main_frame,
            width=440,
            placeholder_text="Вставьте ссылку на YouTube...",
        )
        self.entry_url.pack(pady=5)

        # Контекстное меню по ПКМ
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(
            label="Копировать", command=self.force_copy
        )
        self.context_menu.add_command(
            label="Вставить", command=self.force_paste
        )
        self.context_menu.add_command(
            label="Выделить всё", command=self.force_select_all
        )
        self.entry_url.bind(
            "<Button-3>",
            lambda e: self.context_menu.tk_popup(e.x_root, e.y_root),
        )

        # Привязываем перехват нажатий для гарантированной работы Ctrl+V, Ctrl+C, Ctrl+A при ЛЮБОЙ раскладке
        self.bind_universal_shortcuts()

        # Выбор формата (MP4 / MP3)
        self.format_var = ctk.StringVar(value="mp4")
        self.radio_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.radio_frame.pack(pady=10)

        self.radio_mp4 = ctk.CTkRadioButton(
            self.radio_frame,
            text="MP4 (Видео)",
            variable=self.format_var,
            value="mp4",
        )
        self.radio_mp4.pack(side="left", padx=15)

        self.radio_mp3 = ctk.CTkRadioButton(
            self.radio_frame,
            text="MP3 (Аудио)",
            variable=self.format_var,
            value="mp3",
        )
        self.radio_mp3.pack(side="left", padx=15)

        # Выбор пути скачивания
        self.path_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.path_frame.pack(pady=5, fill="x", padx=30)

        self.entry_path = ctk.CTkEntry(
            self.path_frame, width=320, placeholder_text="Путь сохранения"
        )
        self.entry_path.insert(0, self.save_directory)
        self.entry_path.pack(side="left", padx=(0, 10))

        self.btn_browse = ctk.CTkButton(
            self.path_frame,
            text="Обзор",
            width=90,
            command=self.browse_folder,
        )
        self.btn_browse.pack(side="right")

        # Шкала прогресса
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=440)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(15, 5))

        self.label_percentage = ctk.CTkLabel(
            self.main_frame,
            text="0%",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.label_percentage.pack(pady=2)

        # Кнопка скачивания
        self.btn_download = ctk.CTkButton(
            self.main_frame,
            text="Скачать",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.start_download_thread,
        )
        self.btn_download.pack(pady=10)

        # Статус
        self.label_status = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.label_status.pack(pady=2)

        # Нижний информационный текст со ссылкой
        self.label_footer = ctk.CTkLabel(
            self.main_frame,
            text="Наш Discord: https://discord.gg/RdCuCF6E8",
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color="#1E90FF",
            cursor="hand2",
        )
        self.label_footer.pack(side="bottom", pady=15)
        self.label_footer.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new_tab("https://discord.gg/RdCuCF6E8"),
        )

    # --- Универсальный перехват сочетаний клавиш ---
    def bind_universal_shortcuts(self):
        # Перехватываем событие нажатия любых клавиш в окне
        self.entry_url.bind("<Key>", self.handle_key_press)

    def handle_key_press(self, event):
        # event.state & 4 проверяет зажатую клавишу Ctrl
        # event.keycode == 86 (V в Windows), event.keysym.lower() в других ОС
        if event.state & 4 or event.state & 12:  # Зажат Ctrl
            key = event.keysym.lower()

            # Вставка (V на англ, М на рус)
            if key in ["v", "m", "cyrillic_em"]:
                self.force_paste()
                return "break"

            # Копирование (C на англ, С на рус)
            elif key in ["c", "cyrillic_es"]:
                self.force_copy()
                return "break"

            # Выделить все (A на англ, Ф на рус)
            elif key in ["a", "cyrillic_ef"]:
                self.force_select_all()
                return "break"

    def force_paste(self):
        try:
            # Берём текст напрямую из системного буфера обмена Tkinter
            text = self.clipboard_get()
            if text:
                try:
                    # Если есть выделенный текст, заменяем его
                    self.entry_url.delete(
                        self.entry_url.index("sel.first"),
                        self.entry_url.index("sel.last"),
                    )
                except tk.TclError:
                    pass
                # Вставляем текст в текущую позицию курсора
                self.entry_url.insert(self.entry_url.index("insert"), text)
        except tk.TclError:
            pass  # В буфере обмена нет текста

    def force_copy(self):
        try:
            selected_text = self.entry_url.selection_get()
            if selected_text:
                self.clipboard_clear()
                self.clipboard_append(selected_text)
        except tk.TclError:
            pass

    def force_select_all(self):
        self.entry_url.select_range(0, tk.END)
        self.entry_url.icursor(tk.END)

    # --- Логика выбора папки ---
    def browse_folder(self):
        folder_selected = ctk.filedialog.askdirectory()
        if folder_selected:
            self.save_directory = folder_selected
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, self.save_directory)

    # --- Обновление интерфейса из фонового потока ---
    def update_ui_progress(self, percentage, percent_str):
        self.progress_bar.set(percentage)
        self.label_percentage.configure(text=percent_str)

    def progress_hook(self, d):
        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded_bytes = d.get("downloaded_bytes", 0)

            if total_bytes:
                percentage = downloaded_bytes / total_bytes
                percent_str = f"{int(percentage * 100)}%"
                self.after(
                    0, self.update_ui_progress, percentage, percent_str
                )

        elif d["status"] == "finished":
            self.after(
                0, self.update_ui_progress, 1.0, "100% (Обработка...)"
            )

    # --- Загрузка ---
    def start_download_thread(self):
        url = self.entry_url.get().strip()
        save_path = self.entry_path.get().strip()

        if not url:
            self.label_status.configure(
                text="Пожалуйста, введите ссылку!", text_color="red"
            )
            return

        if not os.path.exists(save_path):
            self.label_status.configure(
                text="Указанный путь не существует!", text_color="red"
            )
            return

        self.btn_download.configure(state="disabled")
        self.btn_browse.configure(state="disabled")
        self.progress_bar.set(0)
        self.label_percentage.configure(text="0%")
        self.label_status.configure(
            text="Загрузка началась...", text_color="yellow"
        )

        threading.Thread(
            target=self.download, args=(url, save_path), daemon=True
        ).start()

    def download(self, url, save_path):
        fmt = self.format_var.get()
        out_template = os.path.join(save_path, "%(title)s.%(ext)s")

        if fmt == "mp3":
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "outtmpl": out_template,
                "progress_hooks": [self.progress_hook],
            }
        else:
            ydl_opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": out_template,
                "progress_hooks": [self.progress_hook],
            }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(
                0,
                lambda: self.label_status.configure(
                    text="Успешно скачано!", text_color="#00FF00"
                ),
            )
            self.after(
                0, lambda: self.label_percentage.configure(text="100%")
            )
        except Exception:
            self.after(
                0,
                lambda: self.label_status.configure(
                    text="Ошибка при скачивании", text_color="red"
                ),
            )
        finally:
            self.after(0, lambda: self.btn_download.configure(state="normal"))
            self.after(0, lambda: self.btn_browse.configure(state="normal"))


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()