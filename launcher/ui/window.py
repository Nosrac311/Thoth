from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
)

from PySide6.QtGui import QIcon

from PySide6.QtCore import QTimer


from launcher.manager import ServiceManager

from launcher.ui.resource import resource_path
from launcher.ui.tray import TrayManager
from launcher.ui.status_panel import StatusPanel
from launcher.ui.tabs import LauncherTabs


class LauncherWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.icon_path = resource_path(
            "launcher/assets/thoth.ico"
        )

        self.setWindowIcon(
            QIcon(self.icon_path)
        )

        self.manager = ServiceManager()

        self.setWindowTitle(
            "Thoth Control Center"
        )

        self.resize(
            1200,
            800
        )

        self.status_panel = StatusPanel(
            self.manager
        )

        self.tabs = LauncherTabs(
            self.status_panel
        )

        layout = QVBoxLayout()

        layout.addWidget(
            self.tabs
        )

        self.setLayout(
            layout
        )

        self.setup_timer()

        self.tray = TrayManager(
            self
        )

    def setup_timer(self):

        QTimer.singleShot(
            500,
            self.manager.start_services
        )

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.status_panel.refresh
        )

        self.timer.start(
            1000
        )

    def open_dashboard(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()
        self.tabs.setCurrentIndex(0)

    def closeEvent(self, event):

        event.ignore()

        self.hide()

        self.tray.showMessage(
            "Thoth Running",
            "Launcher minimized to tray"
        )

    def exit_app(self):

        self.manager.stop_all()

        self.tray.hide()

        QApplication.quit()
