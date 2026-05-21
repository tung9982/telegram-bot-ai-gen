const { app, BrowserWindow, Notification } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({ width: 1600, height: 960, webPreferences: { contextIsolation: true } });
  const devUrl = process.env.VITE_DEV_SERVER_URL;
  if (devUrl) win.loadURL(devUrl); else win.loadFile(path.join(__dirname, '../frontend/dist/index.html'));
  new Notification({ title: 'AetherFlow', body: 'Studio ready.' }).show();
}
app.whenReady().then(createWindow);
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
