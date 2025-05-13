from ttkthemes import ThemedTk
from tkinter import ttk
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import platform
import os
from PIL import Image, ImageTk

try:
    if platform.system() == "Windows":
        import winsound
    else:
        from playsound import playsound
except ImportError:
    print("Instale 'playsound' se estiver fora do Windows: pip install playsound")

class CountdownApp:
    def __init__(self, master):
        self.master = master
        master.title("Pausa para descanso")
        master.geometry("350x300")
        master.minsize(320, 280)
        master.resizable(True, True)

        # Carrega e armazena a imagem original
        self.original_bg1 = Image.open("fundo1.jpg")
        self.bg1 = ImageTk.PhotoImage(self.original_bg1)
        self.bg_label = tk.Label(master, image=self.bg1)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Função para atualizar o fundo ao redimensionar
        def resize_background(event):
            new_width = event.width
            new_height = event.height
            resized = self.original_bg1.resize((new_width, new_height), Image.LANCZOS)
            self.bg1 = ImageTk.PhotoImage(resized)
            self.bg_label.config(image=self.bg1)

        master.bind("<Configure>", resize_background)

        # Solicita a senha inicial
        self.password = simpledialog.askstring(
            "Configurar Senha", "Defina uma senha para desbloquear:",
            show='*', parent=master)
        if not self.password:
            messagebox.showerror("Erro", "Você deve definir uma senha para continuar.")
            master.destroy()
            return

        # Frame principal para centralizar
        frame = ttk.Frame(master, padding=20)
        frame.pack(expand=True, fill="both")

        # Entradas de hora, minuto e segundo
        ttk.Label(frame, text="Horas:").grid(row=0, column=0, sticky="e", pady=5)
        ttk.Label(frame, text="Minutos:").grid(row=1, column=0, sticky="e", pady=5)
        ttk.Label(frame, text="Segundos:").grid(row=2, column=0, sticky="e", pady=5)
        ttk.Label(frame, text="Tempo de bloqueio (min):").grid(row=3, column=0, sticky="e", pady=5)

        self.hour_var = tk.StringVar(value="0")
        self.min_var = tk.StringVar(value="0")
        self.sec_var = tk.StringVar(value="0")
        self.lock_var = tk.StringVar(value="5")

        ttk.Entry(frame, textvariable=self.hour_var, width=8).grid(row=0, column=1)
        ttk.Entry(frame, textvariable=self.min_var, width=8).grid(row=1, column=1)
        ttk.Entry(frame, textvariable=self.sec_var, width=8).grid(row=2, column=1)
        ttk.Entry(frame, textvariable=self.lock_var, width=8).grid(row=3, column=1)

        # Botões iniciar e parar
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        self.start_button = ttk.Button(btn_frame, text="Iniciar", width=10, command=self.start)
        self.start_button.pack(side="left", padx=10)
        self.stop_button = ttk.Button(btn_frame, text="Parar", width=10, command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(side="left", padx=10)

        # Label de contagem regressiva visual
        self.display_label = ttk.Label(frame, text="", font=("Helvetica", 18), foreground="purple")
        self.display_label.grid(row=5, column=0, columnspan=2, pady=10)

        self.running = False
        self.total_seconds = 0
        self.lock_time = int(self.lock_var.get()) * 60  # segundos de bloqueio

    def start(self):
        if self.running:
            return
        try:
            h = int(self.hour_var.get())
            m = int(self.min_var.get())
            s = int(self.sec_var.get())
            lock_min = int(self.lock_var.get())
        except ValueError:
            messagebox.showerror("Entrada Inválida", "Insira números inteiros válidos.")
            return

        self.total_seconds = h * 3600 + m * 60 + s
        if self.total_seconds <= 0:
            messagebox.showwarning("Tempo Inválido", "O tempo deve ser maior que zero.")
            return

        self.lock_time = lock_min * 60
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.running = True
        threading.Thread(target=self.countdown).start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.start_button.config(state=tk.NORMAL, text="Iniciar")
        self.stop_button.config(state=tk.DISABLED)
        self.display_label.config(text="")

    def countdown(self):
        while self.total_seconds > 0 and self.running:
            mins, secs = divmod(self.total_seconds, 60)
            hrs, mins = divmod(mins, 60)
            time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
            self.display_label.config(text=f"Tempo restante: {time_str}")
            self.master.update()
            self.total_seconds -= 1
            threading.Event().wait(1)

        if self.running:
            try:
                if platform.system() == "Windows":
                    winsound.Beep(1000, 500)
                else:
                    playsound(os.path.join(os.path.dirname(__file__), "start.mp3"))
            except:
                print("Erro ao reproduzir som.")

            self.master.after(0, self.lock_screen)

        self.display_label.config(text="Tempo esgotado.")

    def lock_screen(self):
        lock = tk.Toplevel(self.master)
        lock.attributes('-fullscreen', True)
        lock.protocol("WM_DELETE_WINDOW", lambda: None)
        lock.grab_set()

        # Fundo da tela de bloqueio
        fundo2 = Image.open("fundo2.jpg")
        screen_width = lock.winfo_screenwidth()
        screen_height = lock.winfo_screenheight()
        fundo2 = fundo2.resize((screen_width, screen_height))
        self.bg2 = ImageTk.PhotoImage(fundo2)
        bg_label = tk.Label(lock, image=self.bg2)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        container = ttk.Frame(lock, padding=20)
        container.pack(expand=True)

        ttk.Label(container, text="Tempo para descansar! Insira a senha para desbloquear:",
                  font=(None, 24)).pack(pady=20)
        pwd_var = tk.StringVar()
        pwd_entry = ttk.Entry(container, textvariable=pwd_var, show="*", font=(None, 18))
        pwd_entry.pack(pady=10)
        lock.after(100, lambda: pwd_entry.focus())

        unlock_button = ttk.Button(container, text="Desbloquear", command=lambda: try_unlock(), width=15)
        unlock_button.pack(pady=15)

        lock_time_label = ttk.Label(container, text="Desbloqueio em: 00:00", font=(None, 18))
        lock_time_label.pack(pady=10)

        self.locked_seconds = 0

        def update_lock_time():
            if not lock.winfo_exists():
                return
            remaining = self.lock_time - self.locked_seconds
            mins, secs = divmod(remaining, 60)
            lock_time_label.config(text=f"Desbloqueio em: {mins:02d}:{secs:02d}")
            self.locked_seconds += 1
            if remaining <= 0:
                self.running = False
                try:
                    if platform.system() == "Windows":
                        winsound.Beep(1500, 500)
                    else:
                        playsound(os.path.join(os.path.dirname(__file__), "finished.mp3"))
                except:
                    print("Erro ao reproduzir som.")
                lock.destroy()
                self.start_button.config(state=tk.NORMAL, text="Iniciar")
                self.stop_button.config(state=tk.DISABLED)
            else:
                lock.after(1000, update_lock_time)

        def try_unlock(event=None):
            if pwd_var.get() == self.password:
                self.running = False
                lock.destroy()
                self.start_button.config(state=tk.NORMAL, text="Iniciar")
                self.stop_button.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Senha Incorreta", "Senha incorreta. Tente novamente.")
                pwd_var.set("")

        update_lock_time()
        pwd_entry.bind("<Return>", try_unlock)
        lock.update_idletasks()
        lock.geometry(lock.winfo_geometry())

if __name__ == '__main__':
    root = ThemedTk(theme="radiance")
    app = CountdownApp(root)
    root.mainloop()
