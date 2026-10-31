const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("obsidianAPI", {
  isElectron: true,
  platform: process.platform,

  // Native Frameless Window Controls
  minimizeWindow: () => ipcRenderer.invoke("window:minimize"),
  maximizeWindow: () => ipcRenderer.invoke("window:maximize"),
  closeWindow: () => ipcRenderer.invoke("window:close"),

  // Native Local Markdown (.md) + PNG Vault Operations
  getVaultInfo: () => ipcRenderer.invoke("vault:get-info"),
  selectVaultFolder: () => ipcRenderer.invoke("vault:select-folder"),
  openVaultInExplorer: () => ipcRenderer.invoke("vault:open-in-explorer"),
  listVaultNotes: () => ipcRenderer.invoke("vault:list-notes"),
  saveVaultNote: (filename, markdownContent, pngFilename, pngDataUrl) =>
    ipcRenderer.invoke("vault:save-note", { filename, markdownContent, pngFilename, pngDataUrl }),
  readVaultNote: (filename) =>
    ipcRenderer.invoke("vault:read-note", { filename }),
  deleteVaultNote: (filename) =>
    ipcRenderer.invoke("vault:delete-note", { filename }),

  // Native Drag-Out of Right Captured Chart as PNG File
  startDragChartPng: (pngFilename, pngDataUrl) =>
    ipcRenderer.send("chart:start-drag", { pngFilename, pngDataUrl }),

  // Native Electron printToPDF (One-click Landscape PDF with millisecond filename)
  exportLandscapePDF: (defaultFilename) =>
    ipcRenderer.invoke("pdf:export", { defaultFilename })
});
