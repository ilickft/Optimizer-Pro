import os
import shutil
import threading
import subprocess
import winreg
import tkinter.messagebox as messagebox
import customtkinter as ctk

# Configure the modern dark theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("System Optimizer Pro")
        self.geometry("850x550")
        self.resizable(False, False)

        # Configure grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Optimizer Pro", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.tab_temp_btn = ctk.CTkButton(self.sidebar_frame, text="Temp Cleaner", command=lambda: self.select_frame("temp"))
        self.tab_temp_btn.grid(row=1, column=0, padx=20, pady=10)

        self.tab_uninst_btn = ctk.CTkButton(self.sidebar_frame, text="Uninstaller", command=lambda: self.select_frame("uninst"))
        self.tab_uninst_btn.grid(row=2, column=0, padx=20, pady=10)

        self.tab_browser_btn = ctk.CTkButton(self.sidebar_frame, text="Browser Cleaner", command=lambda: self.select_frame("browser"))
        self.tab_browser_btn.grid(row=3, column=0, padx=20, pady=10)

        # --- FRAMES ---
        self.temp_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.setup_temp_frame()

        self.uninst_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.setup_uninst_frame()

        self.browser_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.setup_browser_frame()

        # Select default frame
        self.select_frame("temp")

    def select_frame(self, name):
        # Reset button colors
        self.tab_temp_btn.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "temp" else "transparent")
        self.tab_uninst_btn.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "uninst" else "transparent")
        self.tab_browser_btn.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "browser" else "transparent")

        # Hide all frames
        self.temp_frame.grid_forget()
        self.uninst_frame.grid_forget()
        self.browser_frame.grid_forget()

        # Show selected frame
        if name == "temp":
            self.temp_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        elif name == "uninst":
            self.uninst_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
            self.load_programs()
        elif name == "browser":
            self.browser_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    # --- SHARED UTILITY ---
    def get_dir_size(self, path):
        """Calculates size of a file or directory safely"""
        if not os.path.exists(path): 
            return 0
        if os.path.isfile(path):
            try: return os.path.getsize(path)
            except: return 0
            
        total = 0
        for dp, _, fns in os.walk(path):
            for f in fns:
                fp = os.path.join(dp, f)
                if not os.path.islink(fp):
                    try: total += os.path.getsize(fp)
                    except: pass
        return total

    # ==========================================
    # 1. TEMP CLEANER LOGIC
    # ==========================================
    def setup_temp_frame(self):
        ctk.CTkLabel(self.temp_frame, text="System Temp Cleaner", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 15))
        
        self.t_log_box = ctk.CTkTextbox(self.temp_frame, width=550, height=250, font=ctk.CTkFont(size=13))
        self.t_log_box.pack(pady=10)
        self.t_log_box.insert("0.0", "Click 'Scan' to find junk files.\n\nTargets:\n- %TEMP%\n- C:\\Windows\\Temp\n- C:\\Windows\\Prefetch")
        self.t_log_box.configure(state="disabled")

        self.t_progress = ctk.CTkProgressBar(self.temp_frame, width=550)
        self.t_progress.pack(pady=10)
        self.t_progress.set(0)

        btn_frame = ctk.CTkFrame(self.temp_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.t_scan_btn = ctk.CTkButton(btn_frame, text="Scan Storage", command=self.start_t_scan, font=ctk.CTkFont(weight="bold"))
        self.t_scan_btn.pack(side="left", padx=10)

        self.t_clean_btn = ctk.CTkButton(btn_frame, text="Clean Now", command=self.start_t_clean, state="disabled", fg_color="#A32424", hover_color="#7A1B1B", font=ctk.CTkFont(weight="bold"))
        self.t_clean_btn.pack(side="left", padx=10)

    def start_t_scan(self):
        self.t_scan_btn.configure(state="disabled")
        self.t_clean_btn.configure(state="disabled")
        self.t_progress.configure(mode="indeterminate")
        self.t_progress.start()
        threading.Thread(target=self._t_scan_thread).start()

    def _t_scan_thread(self):
        temp_dir = os.environ.get('TEMP') or ""
        targets = [("User Temp", temp_dir), ("Windows Temp", r"C:\Windows\Temp"), ("Prefetch", r"C:\Windows\Prefetch")]
        log_txt, total_bytes = "--- SCAN RESULTS ---\n\n", 0
        for name, path in targets:
            if path and os.path.exists(path):
                size = self.get_dir_size(path)
                total_bytes += size
                log_txt += f"[{name}]\nSize: {size / (1024*1024):.2f} MB\n\n"
        
        total_mb = total_bytes / (1024*1024)
        log_txt += f"====================\nTOTAL JUNK: {total_mb:.2f} MB"
        self.after(0, lambda: self._t_finish_scan(log_txt, total_mb))

    def _t_finish_scan(self, log, mb):
        self.t_progress.stop()
        self.t_progress.configure(mode="determinate")
        self.t_progress.set(1)
        self.t_log_box.configure(state="normal")
        self.t_log_box.delete("0.0", "end")
        self.t_log_box.insert("end", log)
        self.t_log_box.configure(state="disabled")
        self.t_scan_btn.configure(state="normal", text="Rescan")
        if mb > 0: self.t_clean_btn.configure(state="normal")

    def start_t_clean(self):
        self.t_scan_btn.configure(state="disabled")
        self.t_clean_btn.configure(state="disabled")
        self.t_progress.configure(mode="indeterminate")
        self.t_progress.start()
        threading.Thread(target=self._t_clean_thread).start()

    def _t_clean_thread(self):
        temp_dir = os.environ.get('TEMP') or ""
        targets = [temp_dir, r"C:\Windows\Temp", r"C:\Windows\Prefetch"]
        deleted, freed = 0, 0
        for path in targets:
            if path and os.path.exists(path):
                try:
                    items = os.listdir(path)
                except Exception:
                    continue 
                
                for item in items:
                    ipath = os.path.join(path, item)
                    try:
                        size = self.get_dir_size(ipath)
                        if os.path.isfile(ipath): os.remove(ipath)
                        else: shutil.rmtree(ipath)
                        deleted += 1
                        freed += size
                    except: pass
                    
        msg = f"--- COMPLETE ---\nDeleted {deleted} items.\nFreed {freed / (1024*1024):.2f} MB."
        self.after(0, lambda: self._t_finish_clean(msg))

    def _t_finish_clean(self, msg):
        self.t_progress.stop()
        self.t_progress.configure(mode="determinate")
        self.t_progress.set(1)
        self.t_log_box.configure(state="normal")
        self.t_log_box.delete("0.0", "end")
        self.t_log_box.insert("end", msg)
        self.t_log_box.configure(state="disabled")
        self.t_scan_btn.configure(state="normal")

    # ==========================================
    # 2. UNINSTALLER LOGIC
    # ==========================================
    def setup_uninst_frame(self):
        ctk.CTkLabel(self.uninst_frame, text="Program Uninstaller", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 5))
        ctk.CTkLabel(self.uninst_frame, text="Warning: This triggers the official uninstaller. Admin rights may be required.", text_color="gray").pack(pady=(0, 10))
        self.prog_scroll = ctk.CTkScrollableFrame(self.uninst_frame, width=550, height=350)
        self.prog_scroll.pack(fill="both", expand=True)

    def get_installed_programs(self):
        programs = []
        keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        for hkey, path in keys:
            try:
                key = winreg.OpenKey(hkey, path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey = winreg.OpenKey(key, winreg.EnumKey(key, i))
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        try: cmd = winreg.QueryValueEx(subkey, "QuietUninstallString")[0]
                        except: cmd = winreg.QueryValueEx(subkey, "UninstallString")[0]
                        if name and cmd and name not in [p['name'] for p in programs]:
                            programs.append({"name": name, "cmd": cmd})
                    except: pass
            except: pass
        return sorted(programs, key=lambda x: x['name'].lower())

    def load_programs(self):
        for widget in self.prog_scroll.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.prog_scroll, text="Loading programs...").pack(pady=20)
        self.update()
        programs = self.get_installed_programs()
        for widget in self.prog_scroll.winfo_children(): widget.destroy()
        for prog in programs:
            frame = ctk.CTkFrame(self.prog_scroll)
            frame.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(frame, text=prog['name'], anchor="w").pack(side="left", padx=10, pady=5, fill="x", expand=True)
            ctk.CTkButton(frame, text="Uninstall", width=80, fg_color="#A32424", hover_color="#7A1B1B", 
                          command=lambda n=prog['name'], c=prog['cmd']: self.uninstall_app(n, c)).pack(side="right", padx=10, pady=5)

    def uninstall_app(self, name, cmd):
        if messagebox.askyesno("Confirm Uninstall", f"Uninstall:\n\n{name}?"):
            try:
                subprocess.Popen(cmd, shell=True)
                messagebox.showinfo("Launched", f"Uninstaller launched for {name}.")
            except Exception as e: messagebox.showerror("Error", str(e))

    # ==========================================
    # 3. BROWSER CLEANER LOGIC
    # ==========================================
    def setup_browser_frame(self):
        ctk.CTkLabel(self.browser_frame, text="Browser Data Cleaner", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 5))
        ctk.CTkLabel(self.browser_frame, text="CLOSE YOUR BROWSERS BEFORE CLEANING", text_color="#FFaa00", font=ctk.CTkFont(weight="bold")).pack(pady=(0, 15))

        self.chk_chrome = ctk.BooleanVar(value=True)
        self.chk_edge = ctk.BooleanVar(value=False)
        self.chk_firefox = ctk.BooleanVar(value=False)
        self.chk_brave = ctk.BooleanVar(value=False)
        self.chk_opera = ctk.BooleanVar(value=False)
        
        self.chk_cache = ctk.BooleanVar(value=True)
        self.chk_cookies = ctk.BooleanVar(value=False)
        self.chk_history = ctk.BooleanVar(value=False)

        b_frame = ctk.CTkFrame(self.browser_frame)
        b_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(b_frame, text="Select Browsers:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        b_chk_frame = ctk.CTkFrame(b_frame, fg_color="transparent")
        b_chk_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkCheckBox(b_chk_frame, text="Chrome", variable=self.chk_chrome).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkCheckBox(b_chk_frame, text="Edge", variable=self.chk_edge).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkCheckBox(b_chk_frame, text="Firefox", variable=self.chk_firefox).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkCheckBox(b_chk_frame, text="Brave", variable=self.chk_brave).grid(row=0, column=3, padx=10, pady=5, sticky="w")
        ctk.CTkCheckBox(b_chk_frame, text="Opera", variable=self.chk_opera).grid(row=0, column=4, padx=10, pady=5, sticky="w")

        d_frame = ctk.CTkFrame(self.browser_frame)
        d_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(d_frame, text="Select Data:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkCheckBox(d_frame, text="Cache", variable=self.chk_cache).pack(side="left", padx=20, pady=5)
        ctk.CTkCheckBox(d_frame, text="Cookies", variable=self.chk_cookies).pack(side="left", padx=20, pady=5)
        ctk.CTkCheckBox(d_frame, text="History", variable=self.chk_history).pack(side="left", padx=20, pady=5)

        self.b_log = ctk.CTkTextbox(self.browser_frame, height=120)
        self.b_log.pack(fill="x", pady=15)
        self.b_log.insert("0.0", "Select options and click Scan Browser.")
        self.b_log.configure(state="disabled")

        btn_frame = ctk.CTkFrame(self.browser_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.b_scan_btn = ctk.CTkButton(btn_frame, text="Scan Browsers", command=self.start_b_scan, font=ctk.CTkFont(weight="bold"))
        self.b_scan_btn.pack(side="left", padx=10)

        self.b_clean_btn = ctk.CTkButton(btn_frame, text="Clean Browser Data", state="disabled", fg_color="#A32424", hover_color="#7A1B1B", command=self.start_b_clean, font=ctk.CTkFont(weight="bold"))
        self.b_clean_btn.pack(side="left", padx=10)

    def get_chromium_targets(self, browser_name, user_data_path):
        """Universal helper to extract targets from all profiles in Chromium browsers"""
        targets = []
        if not os.path.exists(user_data_path):
            return targets
        
        try:
            for folder in os.listdir(user_data_path):
                if folder == "Default" or folder.startswith("Profile"):
                    profile_path = os.path.join(user_data_path, folder)
                    profile_name = f"{browser_name} ({folder})"
                    
                    if self.chk_cache.get(): 
                        targets.extend([
                            (f"{profile_name} Cache", os.path.join(profile_path, "Cache")), 
                            (f"{profile_name} Code Cache", os.path.join(profile_path, "Code Cache")),
                            (f"{profile_name} Cache Data", os.path.join(profile_path, r"Cache\Cache_Data"))
                        ])
                    if self.chk_cookies.get(): 
                        targets.append((f"{profile_name} Cookies", os.path.join(profile_path, r"Network\Cookies")))
                    if self.chk_history.get(): 
                        targets.append((f"{profile_name} History", os.path.join(profile_path, "History")))
        except Exception:
            pass
            
        return targets

    def get_browser_targets(self):
        """Generates list of targets based on checkbox selections"""
        local_app = os.environ.get('LOCALAPPDATA') or ""
        roaming_app = os.environ.get('APPDATA') or ""
        targets = []

        if self.chk_chrome.get() and local_app:
            targets.extend(self.get_chromium_targets("Chrome", os.path.join(local_app, r"Google\Chrome\User Data")))

        if self.chk_edge.get() and local_app:
            targets.extend(self.get_chromium_targets("Edge", os.path.join(local_app, r"Microsoft\Edge\User Data")))

        if self.chk_brave.get() and local_app:
            targets.extend(self.get_chromium_targets("Brave", os.path.join(local_app, r"BraveSoftware\Brave-Browser\User Data")))

        if self.chk_opera.get():
            for op_type, folder in [("Opera", "Opera Stable"), ("Opera GX", "Opera GX Stable")]:
                if roaming_app and local_app:
                    base_roam = os.path.join(roaming_app, f"Opera Software\\{folder}")
                    base_loc = os.path.join(local_app, f"Opera Software\\{folder}")
                    if os.path.exists(base_roam) or os.path.exists(base_loc):
                        if self.chk_cache.get(): targets.extend([(f"{op_type} Cache", os.path.join(base_loc, "Cache"))])
                        if self.chk_cookies.get(): targets.append([(f"{op_type} Cookies", os.path.join(base_roam, r"Network\Cookies"))])
                        if self.chk_history.get(): targets.append([(f"{op_type} History", os.path.join(base_roam, "History"))])

        if self.chk_firefox.get():
            if roaming_app and local_app:
                base = os.path.join(roaming_app, r"Mozilla\Firefox\Profiles")
                local_base = os.path.join(local_app, r"Mozilla\Firefox\Profiles")
                if os.path.exists(base):
                    for profile in os.listdir(base):
                        if self.chk_cache.get() and os.path.exists(local_base):
                            targets.append(("Firefox Cache", os.path.join(local_base, profile, "cache2")))
                        if self.chk_cookies.get(): targets.append(("Firefox Cookies", os.path.join(base, profile, "cookies.sqlite")))
                        if self.chk_history.get(): targets.append(("Firefox History", os.path.join(base, profile, "places.sqlite")))
                    
        return targets

    def start_b_scan(self):
        self.b_scan_btn.configure(state="disabled")
        self.b_clean_btn.configure(state="disabled")
        self.b_log.configure(state="normal")
        self.b_log.delete("0.0", "end")
        self.b_log.insert("end", "Scanning browsers...\n")
        self.b_log.configure(state="disabled")
        threading.Thread(target=self._b_scan_thread).start()

    def _b_scan_thread(self):
        targets = self.get_browser_targets()
        total_bytes = 0
        log_txt = "--- BROWSER SCAN RESULTS ---\n\n"
        
        for name, path in targets:
            if os.path.exists(path):
                size = self.get_dir_size(path)
                total_bytes += size
                log_txt += f"{name}: {size / (1024*1024):.2f} MB\n"

        total_mb = total_bytes / (1024*1024)
        log_txt += f"\n====================\nTOTAL TO CLEAN: {total_mb:.2f} MB"
        self.after(0, lambda: self._finish_b_scan(log_txt, total_mb))

    def _finish_b_scan(self, msg, total_mb):
        self.b_log.configure(state="normal")
        self.b_log.delete("0.0", "end")
        self.b_log.insert("end", msg)
        self.b_log.configure(state="disabled")
        self.b_scan_btn.configure(state="normal", text="Rescan")
        if total_mb > 0: self.b_clean_btn.configure(state="normal")

    def start_b_clean(self):
        self.b_scan_btn.configure(state="disabled")
        self.b_clean_btn.configure(state="disabled")
        self.b_log.configure(state="normal")
        self.b_log.delete("0.0", "end")
        self.b_log.insert("end", "Cleaning browsers...\n")
        self.b_log.configure(state="disabled")
        threading.Thread(target=self._b_clean_thread).start()

    def _b_clean_thread(self):
        targets = self.get_browser_targets()
        freed_bytes = 0
        success_count = 0

        for name, path in targets:
            if os.path.exists(path):
                try:
                    size = self.get_dir_size(path)
                    if os.path.isfile(path): os.remove(path)
                    else: shutil.rmtree(path)
                    freed_bytes += size
                    success_count += 1
                except Exception: pass

        msg = f"--- CLEANING COMPLETE ---\nLocations cleared: {success_count}/{len(targets)}\nFreed space: {freed_bytes / (1024*1024):.2f} MB\n\n(If a location wasn't cleared, ensure the browser is fully closed.)"
        self.after(0, lambda: self._finish_b_clean(msg))

    def _finish_b_clean(self, msg):
        self.b_log.configure(state="normal")
        self.b_log.delete("0.0", "end")
        self.b_log.insert("end", msg)
        self.b_log.configure(state="disabled")
        self.b_scan_btn.configure(state="normal")

if __name__ == "__main__":
    app = CleanerApp()
    app.mainloop()