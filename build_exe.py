import os
import sys
import shutil
import zipfile
import subprocess
from generate_icon import generate_ico_file


HIDDEN_IMPORTS = [
    "swisseph",
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
    "fastapi",
    "pydantic",
    "anyio",
    "anyio._backends",
    "anyio._backends._asyncio",
    "starlette",
    "server",
    "main",
    "calc",
    "udhayam",
    "arudam",
    "kavipu",
    "planets",
    "jamma_planets",
    "Schema",
]


def create_payload_zip(source_dir: str, output_zip: str):
    os.makedirs(os.path.dirname(os.path.abspath(output_zip)), exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, source_dir)
                zf.write(abs_path, rel_path)
    print(f"Created compressed application payload: {output_zip} ({os.path.getsize(output_zip) // 1024} KB)")


def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    assets_dir = os.path.join(base_dir, "assets")
    release_dir = os.path.join(base_dir, "release")
    build_dir = os.path.join(base_dir, "build")
    os.makedirs(release_dir, exist_ok=True)

    # 1. Generate Custom Multi-Resolution Windows Icon (.ico)
    icon_path = os.path.join(assets_dir, "app_icon.ico")
    fav_path = os.path.join(static_dir, "favicon.ico")
    generate_ico_file([icon_path, fav_path])

    hidden_args = []
    for mod in HIDDEN_IMPORTS:
        hidden_args.extend(["--hidden-import", mod])

    # 2. Build Fast --onedir Application Bundle (dist/JamakkolHoraStudio/JamakkolHoraStudio.exe)
    print("\n[1/3] Building --onedir application bundle...")
    onedir_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--icon",
        icon_path,
        "--name",
        "JamakkolHoraStudio",
        "--add-data",
        f"{static_dir};static",
        *hidden_args,
        os.path.join(base_dir, "desktop_app.py"),
    ]
    subprocess.check_call(onedir_cmd, cwd=base_dir)

    # 3. Build Single-File Portable EXE (release/JamakkolHoraStudio_Portable.exe)
    print("\n[2/3] Building Single-File Portable Executable (JamakkolHoraStudio_Portable.exe)...")
    portable_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--icon",
        icon_path,
        "--distpath",
        release_dir,
        "--name",
        "JamakkolHoraStudio_Portable",
        "--add-data",
        f"{static_dir};static",
        *hidden_args,
        os.path.join(base_dir, "desktop_app.py"),
    ]
    subprocess.check_call(portable_cmd, cwd=base_dir)

    # 4. Copy Electron runtime & app shell into dist/JamakkolHoraStudio so it never needs Edge
    onedir_dist = os.path.join(base_dir, "dist", "JamakkolHoraStudio")
    electron_src = os.path.join(base_dir, "node_modules", "electron", "dist")
    if os.path.isdir(electron_src):
        print("\n[3/4] Embedding native Electron runtime into dist/JamakkolHoraStudio...")
        electron_dst = os.path.join(onedir_dist, "electron_runtime")
        shutil.copytree(electron_src, electron_dst, dirs_exist_ok=True)
        app_dst = os.path.join(onedir_dist, "electron_app")
        os.makedirs(app_dst, exist_ok=True)
        shutil.copy2(os.path.join(base_dir, "package.json"), os.path.join(app_dst, "package.json"))
        shutil.copytree(os.path.join(base_dir, "electron"), os.path.join(app_dst, "electron"), dirs_exist_ok=True)
        shutil.copytree(os.path.join(base_dir, "assets"), os.path.join(app_dst, "assets"), dirs_exist_ok=True)

    # 5. Package --onedir into app_payload.zip & Build Windows GUI Setup Installer (release/JamakkolHoraStudio_Setup.exe)
    print("\n[4/4] Packaging payload & building Windows GUI Setup Installer (JamakkolHoraStudio_Setup.exe)...")
    payload_zip = os.path.join(build_dir, "app_payload.zip")
    create_payload_zip(onedir_dist, payload_zip)

    setup_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--icon",
        icon_path,
        "--distpath",
        release_dir,
        "--name",
        "JamakkolHoraStudio_Setup",
        "--add-data",
        f"{payload_zip};.",
        "--add-data",
        f"{icon_path};assets",
        os.path.join(base_dir, "installer_setup.py"),
    ]
    subprocess.check_call(setup_cmd, cwd=base_dir)

    print("\n======================================================================")
    print("ZERO-PREREQUISITE BUILD COMPLETE!")
    print(f"1. Setup Installer : {os.path.join(release_dir, 'JamakkolHoraStudio_Setup.exe')}")
    print(f"2. Portable Single : {os.path.join(release_dir, 'JamakkolHoraStudio_Portable.exe')}")
    print(f"3. Fast App Folder : {os.path.join(onedir_dist, 'JamakkolHoraStudio.exe')}")
    print("======================================================================")


if __name__ == "__main__":
    build()
