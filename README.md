# Kakha's Password Vault

A Windows-ready, visually striking desktop password manager that stores credentials with end-to-end encryption entirely on your device.

## Key Features

- **Gorgeous dark-neon interface** optimized for Windows 11 aesthetics with polished gradients, glass-like panels, and custom typography.
- **Zero-knowledge security** – master password is PBKDF2-hashed, and every credential is encrypted with Fernet (AES-128 + HMAC) before touching disk.
- **Local-first storage** using SQLite (no cloud services, no telemetry) so the vault works fully offline.
- **Quality-of-life tools** such as quick add/edit dialogs, inline search-by-sorting, clipboard copy with auto-expire, and inline password reveal prompts.
- **One-click installer script** that builds a standalone `.exe`, deploys it to the Windows desktop, and launches the app automatically.

## Project Structure

```
├── main.py                     # Application entry point
├── vault/
│   ├── app.py                  # QApplication subclass (styling + resource bootstrap)
│   ├── config.py               # App directories + configuration helpers
│   ├── database.py             # SQLite persistence layer
│   ├── security.py             # PBKDF2 hashing + Fernet helpers
│   └── ui/
│       ├── icon_assets.py      # Embedded icon artwork + helpers
│       ├── login.py            # Setup + login flow widgets
│       ├── main_window.py      # Main credential management window
│       └── styles.qss          # Global QSS theme
├── requirements.txt
└── windows_install_and_run.bat # One-click build + desktop deployment script
```

## Running the App (Windows 11)

### 1-click installation & launch

1. Install [Python 3.10+](https://www.python.org/downloads/windows/) if it is not already available on your system.
2. Double-click `windows_install_and_run.bat`.

The batch script will automatically:
- create an isolated virtual environment,
- install all dependencies from `requirements.txt`,
- build a signed-free PyInstaller bundle,
- install the app under `%LOCALAPPDATA%\KakhasPasswordVault`,
- create a desktop shortcut that points to the installed executable, and
- start the application immediately after the build completes.

Future launches are as simple as double-clicking the desktop shortcut the script leaves behind.

### Developer quick start (optional)

```powershell
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

All data is stored under `%APPDATA%\KakhasPasswordVault` (or `~/.KakhasPasswordVault` on other platforms).

## Security Notes

- Master passwords are never stored in plaintext. PBKDF2-HMAC-SHA256 with 390,000 iterations derives both the saved hash and the encryption key.
- Individual credentials are encrypted with Fernet (symmetric AES-128-CBC + HMAC-SHA256). Decryption occurs in-memory only after a successful login.
- Clipboard copies auto-clear after 30 seconds to reduce accidental leaks.

## Packaging Tips

- Icons are embedded directly in `vault/ui/icon_assets.py`. The one-click installer regenerates temporary `.ico`/`.png` files from those assets before invoking PyInstaller so no binary blobs have to be stored in git.
- When adding extra resources (additional QSS, images, etc.), place them under `vault/ui/` and extend the `--add-data` arguments inside `windows_install_and_run.bat` so they are bundled correctly.
- To rebuild manually you can run:

  ```powershell
  python -c "from vault.ui.icon_assets import ensure_icon_files; ensure_icon_files()"
  pyinstaller --noconfirm --windowed --name "KakhasPasswordVault" ^
      --icon "vault\ui\generated\icon.ico" ^
      --add-data "vault\ui\styles.qss;vault\ui" ^
      main.py
  ```

Enjoy safeguarding your secrets with style! 🔐
