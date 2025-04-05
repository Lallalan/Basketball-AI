const path = require('path');
const {  app, BrowserWindow, Menu } = require('electron');

const isDev = process.env.NODE_ENV !== 'production';
const isWindows = process.platform === 'win32';

function createMainWindow() {
    const mainWindow = new BrowserWindow({
        title: 'Team Peak - Sport Fatigue Detector',
        width: isDev ? 1600 : 800,
        height: 600,
    });

    //Open the DevTools if in development mode 
    if (isDev) {
        mainWindow.webContents.openDevTools();
    }
    
    mainWindow.loadFile(path.join(__dirname, './renderer/index.html'));
}

app.whenReady().then(() => {
    createMainWindow();

    const mainMenu = Menu.buildFromTemplate(menu);
    Menu.setApplicationMenu(mainMenu);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createMainWindow();
        }
    })
})

// Menu template
const menu = [
    {
        role: 'fileMenu',
    },
];

app.on('window-all-closed', () => {
    if (!isWindows) {
        app.quit();
    }
})