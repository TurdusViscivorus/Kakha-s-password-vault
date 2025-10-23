from __future__ import annotations

import sys
from vault.app import VaultApp
from vault.config import APP_DIR
from vault.ui.icon_assets import load_app_icon
from vault.ui.login import LoginWindow
from vault.ui.main_window import MainWindow


def main() -> int:
    app = VaultApp(sys.argv)
    APP_DIR.mkdir(parents=True, exist_ok=True)
    app_icon = load_app_icon()
    app.setWindowIcon(app_icon)

    login = LoginWindow(app.config)
    login.setWindowIcon(app_icon)

    def handle_authenticated(fernet) -> None:
        app.set_fernet(fernet)
        app.initialize_database()
        window = MainWindow(app.database, fernet)
        window.setWindowIcon(app_icon)
        window.show()
        login.close()
        app.main_window = window  # type: ignore[attr-defined]

    login.authenticated.connect(handle_authenticated)
    login.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
