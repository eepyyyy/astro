const { app, BrowserWindow, ipcMain, dialog, shell, nativeImage } = require("electron");
const path = require("path");
const fs = require("fs");
const http = require("http");
const net = require("net");
const { spawn } = require("child_process");

let mainWindow = null;
let backendProcess = null;
let backendPort = 8080;

// Persistent Vault Folder path (defaults to HoraryVault inside project or userData)
const ROOT_DIR = path.resolve(__dirname, "..");
let activeVaultDir = path.join(ROOT_DIR, "HoraryVault");

function ensureVaultDirectory() {
  try {
    if (!fs.existsSync(activeVaultDir)) {
      fs.mkdirSync(activeVaultDir, { recursive: true });
    }
  } catch (err) {
    activeVaultDir = path.join(app.getPath("documents"), "JamakkolHoraryVault");
    if (!fs.existsSync(activeVaultDir)) {
      fs.mkdirSync(activeVaultDir, { recursive: true });
    }
  }
}

function checkServerAlive(port) {
  return new Promise((resolve) => {
    const req = http.get(`http://127.0.0.1:${port}/api/vault/info`, { timeout: 900 }, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

function findFreePort(startPort = 8080) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.listen(startPort, "127.0.0.1", () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
    server.on("error", () => {
      resolve(findFreePort(startPort + 1));
    });
  });
}

async function ensurePythonBackend() {
  // 1. If launched by JamakkolHoraStudio.exe with an embedded in-process server port:
  if (process.env.JAMAKKOL_BACKEND_PORT) {
    backendPort = parseInt(process.env.JAMAKKOL_BACKEND_PORT, 10);
    for (let i = 0; i < 150; i++) {
      if (await checkServerAlive(backendPort)) return backendPort;
      await new Promise((r) => setTimeout(r, 200));
    }
    return backendPort;
  }

  // 2. Otherwise (launched via Launch_Obsidian_Desktop.bat or npm start):
  if (await checkServerAlive(8080)) {
    backendPort = 8080;
    return backendPort;
  }
  backendPort = await findFreePort(8080);
  const bundledExe = path.join(process.resourcesPath || ROOT_DIR, "backend", "JamakkolHoraStudio.exe");
  const venvPy = path.join(ROOT_DIR, ".venv", "Scripts", "python.exe");
  const serverScript = path.join(ROOT_DIR, "server.py");

  if (fs.existsSync(bundledExe)) {
    backendProcess = spawn(bundledExe, ["--server-only", String(backendPort)], {
      cwd: path.dirname(bundledExe),
      env: { ...process.env, JAMAKKOL_VAULT_DIR: activeVaultDir },
      stdio: "ignore",
      windowsHide: true
    });
  } else {
    const pythonCmd = fs.existsSync(venvPy) ? venvPy : "python";
    if (fs.existsSync(serverScript)) {
      backendProcess = spawn(pythonCmd, [serverScript, String(backendPort)], {
        cwd: ROOT_DIR,
        env: { ...process.env, JAMAKKOL_VAULT_DIR: activeVaultDir },
        stdio: "ignore",
        windowsHide: true
      });
    }
  }

  // Wait up to 45 seconds for backend to respond
  for (let i = 0; i < 225; i++) {
    const ok = await checkServerAlive(backendPort);
    if (ok) return backendPort;
    await new Promise((r) => setTimeout(r, 200));
  }
  return backendPort;
}

async function createWindow() {
  ensureVaultDirectory();

  mainWindow = new BrowserWindow({
    width: 1620,
    height: 960,
    minWidth: 1100,
    minHeight: 700,
    frame: false,
    show: false,
    backgroundColor: "#111114",
    icon: path.join(ROOT_DIR, "assets", "app_icon.ico"),
    title: "Jamakkol Hora Studio — Obsidian Desktop",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    mainWindow.focus();
  });

  // Show native frameless Electron window immediately with dark Obsidian splash
  const splashHtml = `data:text/html;charset=utf-8,${encodeURIComponent(`<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Jamakkol Hora Studio</title></head>
<body style="margin:0;height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#111114;color:#e4e4e7;font-family:'Segoe UI',system-ui,sans-serif;user-select:none;">
  <div style="font-size:22px;font-weight:700;color:#a78bfa;letter-spacing:1.5px;margin-bottom:10px;">◆ JAMAKKOL HORA STUDIO</div>
  <div style="font-size:13px;color:#9ca3af;">Initializing Swiss Ephemeris &amp; Local Obsidian Markdown Vault...</div>
</body>
</html>`)}`;
  mainWindow.loadURL(splashHtml);

  const port = await ensurePythonBackend();
  if (mainWindow) {
    mainWindow.loadURL(`http://127.0.0.1:${port}/?electron=1`);
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

// ============================================================================
// IPC HANDLERS: FRAMELESS WINDOW CONTROLS
// ============================================================================

ipcMain.handle("window:minimize", () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.handle("window:maximize", () => {
  if (!mainWindow) return false;
  if (mainWindow.isMaximized()) {
    mainWindow.unmaximize();
    return false;
  } else {
    mainWindow.maximize();
    return true;
  }
});

ipcMain.handle("window:close", () => {
  if (mainWindow) mainWindow.close();
});

// ============================================================================
// IPC HANDLERS: LOCAL MARKDOWN (.md) VAULT FILESYSTEM
// ============================================================================

ipcMain.handle("vault:get-info", () => {
  ensureVaultDirectory();
  return {
    vault_dir: activeVaultDir,
    vault_name: path.basename(activeVaultDir)
  };
});

ipcMain.handle("vault:select-folder", async () => {
  if (!mainWindow) return null;
  const result = await dialog.showOpenDialog(mainWindow, {
    title: "Select Local Obsidian Markdown Vault Folder",
    defaultPath: activeVaultDir,
    properties: ["openDirectory", "createDirectory"]
  });
  if (!result.canceled && result.filePaths && result.filePaths.length > 0) {
    activeVaultDir = result.filePaths[0];
    ensureVaultDirectory();
  }
  return {
    vault_dir: activeVaultDir,
    vault_name: path.basename(activeVaultDir)
  };
});

ipcMain.handle("vault:open-in-explorer", async () => {
  ensureVaultDirectory();
  await shell.openPath(activeVaultDir);
  return { ok: true };
});

ipcMain.handle("vault:list-notes", () => {
  ensureVaultDirectory();
  const files = fs.readdirSync(activeVaultDir);
  const notes = [];
  for (const fname of files) {
    if (fname.toLowerCase().endsWith(".md")) {
      const fpath = path.join(activeVaultDir, fname);
      try {
        const stat = fs.statSync(fpath);
        const content = fs.readFileSync(fpath, "utf-8");
        notes.push({
          filename: fname,
          title: fname.slice(0, -3),
          mtime: stat.mtimeMs / 1000,
          size: stat.size,
          preview: content.slice(0, 320)
        });
      } catch (e) {
        // ignore unreadable file
      }
    }
  }
  notes.sort((a, b) => b.mtime - a.mtime);
  return { vault_dir: activeVaultDir, notes };
});

ipcMain.handle("vault:save-note", (_event, { filename, markdownContent, pngFilename, pngDataUrl }) => {
  ensureVaultDirectory();
  let safeName = String(filename || "Horary_Moment")
    .replace(/[^a-zA-Z0-9._\- ]/g, "_")
    .trim();
  if (!safeName.toLowerCase().endsWith(".md")) {
    safeName += ".md";
  }
  const fpath = path.join(activeVaultDir, safeName);
  fs.writeFileSync(fpath, markdownContent, "utf-8");

  let pngPath = null;
  if (pngDataUrl && String(pngDataUrl).startsWith("data:image/png;base64,")) {
    let safePng = String(pngFilename || safeName.slice(0, -3) + ".png")
      .replace(/[^a-zA-Z0-9._\- ]/g, "_")
      .trim();
    if (!safePng.toLowerCase().endsWith(".png")) {
      safePng += ".png";
    }
    pngPath = path.join(activeVaultDir, safePng);
    const b64 = String(pngDataUrl).split(",")[1];
    fs.writeFileSync(pngPath, Buffer.from(b64, "base64"));
  }
  return { ok: true, filename: safeName, path: fpath, pngPath };
});

ipcMain.on("chart:start-drag", (event, { pngFilename, pngDataUrl }) => {
  try {
    ensureVaultDirectory();
    if (!pngDataUrl || !String(pngDataUrl).startsWith("data:image/png;base64,")) return;
    let safePng = String(pngFilename || "Chart.png")
      .replace(/[^a-zA-Z0-9._\- ]/g, "_")
      .trim();
    if (!safePng.toLowerCase().endsWith(".png")) {
      safePng += ".png";
    }
    const pngPath = path.join(activeVaultDir, safePng);
    const b64 = String(pngDataUrl).split(",")[1];
    fs.writeFileSync(pngPath, Buffer.from(b64, "base64"));

    const fullImg = nativeImage.createFromDataURL(pngDataUrl);
    const dragIcon = fullImg.resize({ width: 140, height: 140 });
    event.sender.startDrag({
      file: pngPath,
      icon: dragIcon
    });
  } catch (err) {
    console.error("chart:start-drag error:", err);
  }
});

ipcMain.handle("vault:read-note", (_event, { filename }) => {
  ensureVaultDirectory();
  const safeName = path.basename(String(filename || ""));
  const fpath = path.join(activeVaultDir, safeName);
  if (!fs.existsSync(fpath)) {
    throw new Error("Markdown note not found in Vault");
  }
  const content = fs.readFileSync(fpath, "utf-8");
  return { filename: safeName, path: fpath, markdown_content: content };
});

ipcMain.handle("vault:delete-note", (_event, { filename }) => {
  ensureVaultDirectory();
  const safeName = path.basename(String(filename || ""));
  const fpath = path.join(activeVaultDir, safeName);
  if (fs.existsSync(fpath)) {
    fs.unlinkSync(fpath);
  }
  return { ok: true, deleted: safeName };
});

// ============================================================================
// IPC HANDLER: NATIVE ELECTRON printToPDF (LANDSCAPE SINGLE PAGE)
// ============================================================================

ipcMain.handle("pdf:export", async (_event, { defaultFilename }) => {
  if (!mainWindow) return { ok: false };
  const cleanName = String(defaultFilename || "Horary_Report")
    .replace(/[<>:"/\\|?*]/g, "-")
    .trim();
  const finalPdfName = cleanName.toLowerCase().endsWith(".pdf")
    ? cleanName
    : `${cleanName}.pdf`;

  const saveRes = await dialog.showSaveDialog(mainWindow, {
    title: "Save Landscape Horary Chart PDF",
    defaultPath: path.join(activeVaultDir, finalPdfName),
    filters: [{ name: "PDF Document", extensions: ["pdf"] }]
  });

  if (saveRes.canceled || !saveRes.filePath) {
    return { ok: false, canceled: true };
  }

  const pdfBuffer = await mainWindow.webContents.printToPDF({
    landscape: true,
    printBackground: true,
    pageSize: "A4",
    margins: {
      top: 0.15,
      bottom: 0.15,
      left: 0.2,
      right: 0.2
    }
  });

  fs.writeFileSync(saveRes.filePath, pdfBuffer);
  return { ok: true, filePath: saveRes.filePath };
});

// ============================================================================
// APP LIFECYCLE
// ============================================================================

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (backendProcess) {
    try {
      backendProcess.kill();
    } catch (e) { }
  }
  if (process.platform !== "darwin") {
    app.quit();
  }
});
