from PySide6.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
)

from PySide6.QtGui import QAction, QIcon


class TrayManager:

    def __init__(self, window):

        self.window = window

        self.tray = QSystemTrayIcon(window)

        self.tray.setToolTip(
            "Thoth Control Center"
        )

        self.tray.setIcon(
            QIcon(
                window.icon_path
            )
        )

        self.create_menu()

        self.tray.show()

    def create_menu(self):

        menu = QMenu()

        show = QAction(
            "Show Window",
            self.window
        )

        status = QAction(
            "Status",
            self.window
        )

        exit_action = QAction(
            "Exit",
            self.window
        )

        menu.addAction(show)
        menu.addAction(status)
        menu.addSeparator()
        menu.addAction(exit_action)

        show.triggered.connect(
            self.window.open_dashboard
        )

        status.triggered.connect(
            lambda:
            self.window.tabs.setCurrentIndex(1)
        )

        exit_action.triggered.connect(
            self.window.exit_app
        )

        self.tray.setContextMenu(menu)

    def showMessage(self, title, message):

        self.tray.showMessage(
            title,
            message
        )

    def hide(self):
        self.tray.hide()

    def show(self):
        self.tray.show()
