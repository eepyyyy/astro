import os
import sys
import shutil
import zipfile
import tempfile
import threading
import subprocess
import winreg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


APP_NAME = "Jamakkol Hora Studio"
APP_EXE_NAME = "JamakkolHoraStudio.exe"
APP_VERSION = "2.0.0"
APP_PUBLISHER = "Vedic Horary Studio"
UNINSTALL_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\JamakkolHoraStudio"


def get_bundle_dir() -> str:
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def get_default_install_dir() -> str:
    local_appdata = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
    return os.path.join(local_appdata, "Programs", "JamakkolHoraStudio")


def create_windows_shortcut(shortcut_path: str, target_exe: str, working_dir: str, icon_path: str, description: str):
    vbs_content = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{shortcut_path}")
oLink.TargetPath = "{target_exe}"
oLink.WorkingDirectory = "{working_dir}"
oLink.IconLocation = "{icon_path}, 0"
oLink.Description = "{description}"
oLink.Save
'''
    vbs_file = os.path.join(tempfile.gettempdir(), "create_jamakkol_shortcut.vbs")
    with open(vbs_file, "w", encoding="utf-8") as f:
        f.write(vbs_content.strip())
    try:
        subprocess.run(
            ["cscript", "//Nologo", vbs_file],
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
    finally:
        if os.path.exists(vbs_file):
            try:
                os.remove(vbs_file)
            except OSError:
                pass


def register_uninstaller(install_dir: str, exe_path: str, icon_path: str):
    uninstaller_bat = os.path.join(install_dir, "Uninstall_JamakkolHoraStudio.bat")
    desktop_lnk = os.path.join(os.path.expanduser("~"), "Desktop", f"{APP_NAME}.lnk")
    start_menu_lnk = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs",
        f"{APP_NAME}.lnk",
    )

    bat_content = f'''@echo off
echo Uninstalling {APP_NAME}...
taskkill /F /IM "{APP_EXE_NAME}" >nul 2>&1
del /F /Q "{desktop_lnk}" >nul 2>&1
del /F /Q "{start_menu_lnk}" >nul 2>&1
reg delete "HKCU\\{UNINSTALL_REG_KEY}" /f >nul 2>&1
cd /d "%TEMP%"
rmdir /S /Q "{install_dir}" >nul 2>&1
echo Uninstalled successfully.
'''
    with open(uninstaller_bat, "w", encoding="utf-8") as f:
        f.write(bat_content)

    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_REG_KEY) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, APP_PUBLISHER)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_bat}"')
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
    except Exception:
        pass


def perform_installation(
    install_dir: str,
    make_desktop_shortcut: bool = True,
    make_start_menu_shortcut: bool = True,
    progress_callback=None,
) -> str:
    bundle_dir = get_bundle_dir()
    payload_zip = os.path.join(bundle_dir, "app_payload.zip")
    if not os.path.exists(payload_zip):
        payload_zip = os.path.join(bundle_dir, "build", "app_payload.zip")

    if not os.path.exists(payload_zip):
        raise FileNotFoundError(f"Installer payload not found: {payload_zip}")

    os.makedirs(install_dir, exist_ok=True)

    with zipfile.ZipFile(payload_zip, "r") as zf:
        members = zf.infolist()
        total = max(len(members), 1)
        for idx, member in enumerate(members, 1):
            zf.extract(member, install_dir)
            if progress_callback:
                progress_callback(int(idx * 90 / total), f"Extracting: {member.filename}")

    # Copy icon file
    src_icon = os.path.join(bundle_dir, "assets", "app_icon.ico")
    dst_icon = os.path.join(install_dir, "app_icon.ico")
    if os.path.exists(src_icon):
        shutil.copy2(src_icon, dst_icon)

    target_exe = os.path.join(install_dir, APP_EXE_NAME)

    if progress_callback:
        progress_callback(94, "Creating shortcuts...")

    if make_desktop_shortcut:
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.isdir(desktop_dir):
            lnk_path = os.path.join(desktop_dir, f"{APP_NAME}.lnk")
            create_windows_shortcut(
                lnk_path,
                target_exe,
                install_dir,
                dst_icon if os.path.exists(dst_icon) else target_exe,
                "Jamakkol Prasanam & Hora Chart Studio (Millisecond Precision)",
            )

    if make_start_menu_shortcut:
        programs_dir = os.path.join(
            os.environ.get("APPDATA", ""),
            r"Microsoft\Windows\Start Menu\Programs",
        )
        if os.path.isdir(programs_dir):
            lnk_path = os.path.join(programs_dir, f"{APP_NAME}.lnk")
            create_windows_shortcut(
                lnk_path,
                target_exe,
                install_dir,
                dst_icon if os.path.exists(dst_icon) else target_exe,
                "Jamakkol Prasanam & Hora Chart Studio (Millisecond Precision)",
            )

    if progress_callback:
        progress_callback(98, "Registering application...")

    register_uninstaller(install_dir, target_exe, dst_icon if os.path.exists(dst_icon) else target_exe)

    if progress_callback:
        progress_callback(100, "Installation complete!")

    return target_exe


class ObsidianSetupWizard:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION} — Setup Wizard")
        self.root.geometry("580x420")
        self.root.resizable(False, False)
        self.root.configure(bg="#16161a")

        icon_path = os.path.join(get_bundle_dir(), "assets", "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self.install_dir_var = tk.StringVar(value=get_default_install_dir())
        self.desktop_shortcut_var = tk.BooleanVar(value=True)
        self.startmenu_shortcut_var = tk.BooleanVar(value=True)
        self.launch_after_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready to install (Zero prerequisites required).")
        self.installed_exe_path = None

        self._build_ui()

    def _build_ui(self):
        # Top Header Banner
        header = tk.Frame(self.root, bg="#111114", height=76, highlightthickness=1, highlightbackground="#31313a")
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title_lbl = tk.Label(
            header,
            text="◆ JAMAKKOL HORA STUDIO",
            font=("Segoe UI", 15, "bold"),
            fg="#a78bfa",
            bg="#111114",
        )
        title_lbl.pack(anchor="w", padx=22, pady=(14, 2))

        sub_lbl = tk.Label(
            header,
            text="Obsidian Horary Split Workspace • 1ms (.mmm) Precision • Standalone Edition",
            font=("Segoe UI", 9),
            fg="#9ca3af",
            bg="#111114",
        )
        sub_lbl.pack(anchor="w", padx=24)

        # Main Body Frame
        body = tk.Frame(self.root, bg="#16161a", padx=24, pady=18)
        body.pack(fill="both", expand=True)

        dir_lbl = tk.Label(
            body,
            text="Installation Folder:",
            font=("Segoe UI", 10, "bold"),
            fg="#e4e4e7",
            bg="#16161a",
        )
        dir_lbl.pack(anchor="w", pady=(0, 6))

        dir_row = tk.Frame(body, bg="#16161a")
        dir_row.pack(fill="x", pady=(0, 14))

        dir_entry = tk.Entry(
            dir_row,
            textvariable=self.install_dir_var,
            font=("Consolas", 9),
            bg="#222228",
            fg="#e4e4e7",
            insertbackground="#e4e4e7",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#31313a",
            highlightcolor="#8b5cf6",
        )
        dir_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        browse_btn = tk.Button(
            dir_row,
            text="Browse...",
            command=self._browse_dir,
            font=("Segoe UI", 9, "bold"),
            bg="#2a2a32",
            fg="#e4e4e7",
            activebackground="#3f3f4e",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
        )
        browse_btn.pack(side="right")

        # Options Checkboxes
        chk_style = {
            "font": ("Segoe UI", 9),
            "bg": "#16161a",
            "fg": "#e4e4e7",
            "selectcolor": "#222228",
            "activebackground": "#16161a",
            "activeforeground": "#a78bfa",
            "cursor": "hand2",
        }

        tk.Checkbutton(
            body,
            text="Create Desktop Shortcut (Jamakkol Hora Studio)",
            variable=self.desktop_shortcut_var,
            **chk_style,
        ).pack(anchor="w", pady=2)

        tk.Checkbutton(
            body,
            text="Create Windows Start Menu Shortcut",
            variable=self.startmenu_shortcut_var,
            **chk_style,
        ).pack(anchor="w", pady=2)

        tk.Checkbutton(
            body,
            text="Launch Jamakkol Hora Studio immediately after installation",
            variable=self.launch_after_var,
            **chk_style,
        ).pack(anchor="w", pady=2)

        # Progress Bar & Status
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Obsidian.Horizontal.TProgressbar",
            troughcolor="#222228",
            background="#7c3aed",
            bordercolor="#31313a",
            lightcolor="#8b5cf6",
            darkcolor="#6d28d9",
            thickness=14,
        )

        self.progress = ttk.Progressbar(
            body,
            style="Obsidian.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=100,
        )
        self.progress.pack(fill="x", pady=(18, 6))

        status_lbl = tk.Label(
            body,
            textvariable=self.status_var,
            font=("Consolas", 8),
            fg="#9ca3af",
            bg="#16161a",
            anchor="w",
        )
        status_lbl.pack(fill="x")

        # Footer Buttons
        footer = tk.Frame(self.root, bg="#111114", height=56, highlightthickness=1, highlightbackground="#31313a")
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.cancel_btn = tk.Button(
            footer,
            text="Cancel",
            command=self.root.destroy,
            font=("Segoe UI", 9, "bold"),
            bg="#2a2a32",
            fg="#e4e4e7",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
        )
        self.cancel_btn.pack(side="right", padx=(8, 22), pady=10)

        self.install_btn = tk.Button(
            footer,
            text="Install Now",
            command=self._start_install,
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed",
            fg="#ffffff",
            activebackground="#8b5cf6",
            activeforeground="#ffffff",
            relief="flat",
            padx=22,
            pady=6,
            cursor="hand2",
        )
        self.install_btn.pack(side="right", pady=10)

    def _browse_dir(self):
        chosen = filedialog.askdirectory(initialdir=self.install_dir_var.get(), title="Select Installation Folder")
        if chosen:
            self.install_dir_var.set(os.path.normpath(chosen))

    def _update_progress(self, pct: int, msg: str):
        self.root.after(0, lambda: (self.progress.configure(value=pct), self.status_var.set(msg)))

    def _start_install(self):
        self.install_btn.configure(state="disabled", text="Installing...")
        self.cancel_btn.configure(state="disabled")
        target_dir = self.install_dir_var.get().strip()

        def worker():
            try:
                exe_path = perform_installation(
                    install_dir=target_dir,
                    make_desktop_shortcut=self.desktop_shortcut_var.get(),
                    make_start_menu_shortcut=self.startmenu_shortcut_var.get(),
                    progress_callback=self._update_progress,
                )
                self.installed_exe_path = exe_path
                self.root.after(0, self._on_install_success)
            except Exception as exc:
                self.root.after(0, lambda: self._on_install_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_install_success(self):
        self.install_btn.configure(state="normal", text="Finish", bg="#10b981", command=self._finish_and_close)
        self.cancel_btn.configure(state="normal", text="Close")

    def _on_install_error(self, err_msg: str):
        self.status_var.set(f"Error: {err_msg}")
        self.install_btn.configure(state="normal", text="Retry Install")
        self.cancel_btn.configure(state="normal")
        messagebox.showerror("Installation Failed", f"An error occurred during installation:\n\n{err_msg}")

    def _finish_and_close(self):
        if self.launch_after_var.get() and self.installed_exe_path and os.path.exists(self.installed_exe_path):
            subprocess.Popen([self.installed_exe_path], cwd=os.path.dirname(self.installed_exe_path))
        self.root.destroy()


def main():
    if "--silent" in sys.argv:
        perform_installation(get_default_install_dir(), True, True)
        return

    root = tk.Tk()
    ObsidianSetupWizard(root)
    root.mainloop()


if __name__ == "__main__":
    main()

