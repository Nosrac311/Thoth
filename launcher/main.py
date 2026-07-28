import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from launcher.ui.window import LauncherWindow
from launcher.ui.resource import resource_path

from database.setup import initialize_database


def main():

    app = QApplication(sys.argv)

    app.setWindowIcon(
        QIcon(
            resource_path(
                "launcher/assets/thoth.ico"
            )
        )
    )

    initialize_database()

    window = LauncherWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
