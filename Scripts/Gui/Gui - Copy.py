import customtkinter as ctk
import subprocess
import threading
import os
from pathlib import Path
import sys
import re

if getattr(sys, 'frozen', False):
    base_dir = Path(sys.executable).resolve().parent
else:
    base_dir = Path(__file__).resolve().parent.parent.parent

# Point directly to your embedded portable Python runtime
python_executable = base_dir / "Runtime" / "python.exe"

txt_dir = base_dir / "Txt Files"
YoutubeLinks = txt_dir / "youtube_links.txt"
AnimeDetect = txt_dir / "anime_detect.txt"
AnimeNames = txt_dir / "anime_names.txt"

scripts_dir = base_dir / "Scripts"
LinkCopier = scripts_dir / "LinkCopier" / "LinkCopier.py"
YoutubeDownloader = scripts_dir / "YoutubeDownloader" / "YoutubeDownloader.py"
VidHandler = scripts_dir / "VidHandler" / "VidHandler.py"

class TerminalGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VidHandler Control Panel")
        self.geometry("1100x700")
        
        self.pages = {
            "Page 1": {
                "left": YoutubeLinks,
                "right": "terminal"
            },
            "Page 2": {
                "left": AnimeDetect,
                "right": AnimeNames
            }
        }
        
        self.current_page = "Page 1"
        self.last_mtimes = {"left": 0, "right": 0}
        self.is_progress_line_active = False

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT COLUMN ---
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.editor_left = ctk.CTkTextbox(self.left_frame)
        self.editor_left.pack(pady=10, padx=10, fill="both", expand=True)
        self.editor_left.bind("<KeyRelease>", lambda e: self.save_content(self.editor_left, self.pages[self.current_page]["left"], "left"))

        # --- RIGHT COLUMN ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.content_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.content_container.pack(side="top", fill="both", expand=True)

        self.bottom_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.bottom_container.pack(side="bottom", fill="x", pady=5, padx=10)

        # 1. The Terminal
        self.terminal = ctk.CTkTextbox(self.content_container)
        self.terminal.configure(state="disabled")

        # 2. The Right Editor
        self.editor_right = ctk.CTkTextbox(self.content_container)
        self.editor_right.bind("<KeyRelease>", lambda e: self.save_content(self.editor_right, self.pages[self.current_page]["right"], "right"))

        # --- BUTTONS ---
        self.action_frame = ctk.CTkFrame(self.bottom_container, fg_color="transparent")
        self.action_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkButton(self.action_frame, text="Link Copier", command=lambda: self.start_script_thread(LinkCopier)).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(self.action_frame, text="Youtube Downloader", command=lambda: self.start_script_thread(YoutubeDownloader)).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(self.action_frame, text="VidHandler", command=lambda: self.start_script_thread(VidHandler)).pack(side="left", padx=5, expand=True, fill="x")

        self.page_nav_frame = ctk.CTkFrame(self.bottom_container, fg_color="transparent")
        self.page_nav_frame.pack(fill="x")
        for page_name in self.pages.keys():
            ctk.CTkButton(self.page_nav_frame, text=page_name, command=lambda p=page_name: self.switch_page(p)).pack(side="left", pady=5, padx=5, expand=True, fill="x")

        # --- QUALITY SELECTOR FRAME ---
        self.quality_var = ctk.StringVar(value="360p")
        self.quality_dropdown = ctk.CTkComboBox(
            self.page_nav_frame,
            values=["144p", "360p", "480p", "720p", "1080p"],
            variable=self.quality_var,
            state="readonly",
            width=85
        )
        self.quality_dropdown.pack(side="left", padx=5)

        self.switch_page("Page 1")
        self.monitor_file()

    # --- LOGIC ---
    def monitor_file(self):
        """Checks every 1000ms if the files on disk have changed."""
        path_left = self.pages[self.current_page]["left"]
        if os.path.exists(path_left):
            mtime = os.path.getmtime(path_left)
            if mtime > self.last_mtimes["left"]:
                if self.focus_get() != self.editor_left:
                    self.load_single_file(self.editor_left, path_left, "left")
                else:
                    self.last_mtimes["left"] = mtime

        path_right = self.pages[self.current_page]["right"]
        if path_right != "terminal" and os.path.exists(path_right):
            mtime = os.path.getmtime(path_right)
            if mtime > self.last_mtimes["right"]:
                if self.focus_get() != self.editor_right:
                    self.load_single_file(self.editor_right, path_right, "right")
                else:
                    self.last_mtimes["right"] = mtime
                
        self.after(1000, self.monitor_file)

    def switch_page(self, page_name):
        self.current_page = page_name
        self.terminal.pack_forget()
        self.editor_right.pack_forget()
        
        right_mode = self.pages[page_name]["right"]
        if right_mode == "terminal":
            self.terminal.pack(in_=self.content_container, pady=10, padx=10, fill="both", expand=True)
        else:
            self.editor_right.pack(in_=self.content_container, pady=10, padx=10, fill="both", expand=True)
            
        self.load_single_file(self.editor_left, self.pages[self.current_page]["left"], "left")
        if right_mode != "terminal":
            self.load_single_file(self.editor_right, right_mode, "right")

    def load_single_file(self, widget, path, key):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                widget.delete("1.0", "end")
                widget.insert("1.0", f.read())
            self.last_mtimes[key] = os.path.getmtime(path)

    def save_content(self, widget, path, key):
        if path != "terminal":
            with open(path, "w", encoding="utf-8") as f:
                f.write(widget.get("1.0", "end-1c"))
            self.last_mtimes[key] = os.path.getmtime(path)

    def append_or_update_progress(self, text, is_progress=False):
        self.terminal.configure(state="normal")
        if is_progress:
            if self.is_progress_line_active:
                self.terminal.delete("end-2l", "end-1c")
            self.terminal.insert("end", text + "\n")
            self.is_progress_line_active = True
        else:
            self.terminal.insert("end", text)
            self.is_progress_line_active = False
        self.terminal.see("end")
        self.terminal.configure(state="disabled")

    def start_script_thread(self, script_path):
        if self.pages[self.current_page]["right"] != "terminal":
            self.switch_page("Page 1")
            
        self.save_content(self.editor_left, self.pages[self.current_page]["left"], "left")
        
        self.terminal.configure(state="normal")
        self.terminal.delete("1.0", "end")
        self.terminal.configure(state="disabled")
        self.is_progress_line_active = False
        
        # Collect extra arguments if running the YouTube Downloader
        extra_args = []
        if script_path == YoutubeDownloader:
            extra_args = [self.quality_var.get()]
            
        threading.Thread(target=self.run_script, args=(script_path, extra_args), daemon=True).start()

    def run_script(self, script_path, extra_args=[]):
        my_env = os.environ.copy()
        my_env["FORCE_TERMINAL"] = "1"
        my_env["FORCE_COLOR"] = "1"
        my_env["PYTHONUNBUFFERED"] = "1"
        
        startup_flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
        
        try:
            cmd = [str(python_executable), str(script_path)] + extra_args
            process = subprocess.Popen(
                cmd,  
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                bufsize=1,
                env=my_env,
                creationflags=startup_flags
            )
            
            for line in process.stdout:
                clean_line = line.replace('\r', '\n')
                
                if "[download]" in clean_line and "%" in clean_line and "of" in clean_line and "ETA" in clean_line:
                    match = re.search(r'([\d.]+)%\s+of\s+([^\s]+)\s+at\s+([^\s]+)\s+ETA\s+([^\s]+)', clean_line)
                    if match:
                        pct_str, total_str, speed_str, eta_str = match.groups()
                        try:
                            pct = float(pct_str)
                            
                            def parse_to_bytes(s):
                                m = re.search(r'([\d.]+)([KkMmGgTt]?i?B)?', s)
                                if not m: return 0.0
                                val = float(m.group(1))
                                unit = (m.group(2) or '').upper()
                                mult = 1
                                if 'K' in unit: mult = 1024
                                elif 'M' in unit: mult = 1024 * 1024
                                elif 'G' in unit: mult = 1024 * 1024 * 1024
                                elif 'T' in unit: mult = 1024 * 1024 * 1024 * 1024
                                return val * mult

                            total_bytes = parse_to_bytes(total_str)
                            downloaded_bytes = total_bytes * (pct / 100.0)
                            
                            total_mb = total_bytes / (1024 * 1024)
                            downloaded_mb = downloaded_bytes / (1024 * 1024)
                            
                            speed_bytes = parse_to_bytes(speed_str.replace('/s', ''))
                            speed_mb = speed_bytes / (1024 * 1024)
                            
                            bar_len = 20
                            filled = int(pct / 100 * bar_len)
                            bar = f"Downloading [{'-' * filled}{' ' * (bar_len - filled)}] {pct:.1f}% | {downloaded_mb:.1f}MB/{total_mb:.1f}MB | {speed_mb:.1f}MB/s | ETA {eta_str}"
                            
                            self.after(0, lambda b=bar: self.append_or_update_progress(b, is_progress=True))
                            continue
                        except Exception:
                            pass
                
                self.after(0, lambda l=clean_line: self.append_or_update_progress(l, is_progress=False))
                
            process.wait()
            self.after(0, lambda: self.append_or_update_progress("\n[Process Finished]\n", is_progress=False))
            
        except Exception as e:
            self.after(0, lambda: self.append_or_update_progress(f"\nError: {str(e)}\n", is_progress=False))

if __name__ == "__main__":
    app = TerminalGUI()
    app.mainloop()