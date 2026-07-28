from PySide6.QtWidgets import (
    QTabWidget,
    QWidget,
)

from launcher.ui.dashboard import DashboardWidget
from launcher.ui.channels import ChannelsWidget
from launcher.ui.watchlist import WatchlistWidget


class LauncherTabs(QTabWidget):

    def __init__(self, status_panel):

        super().__init__()

        self.dashboard = DashboardWidget()

        self.status = status_panel

        self.channels = ChannelsWidget()

        self.watchlist = WatchlistWidget()

        self.addTab(
            self.dashboard,
            "Dashboard"
        )

        self.addTab(
            self.status,
            "Status"
        )

        self.addTab(
            self.channels,
            "Channels"
        )

        self.addTab(
            self.watchlist,
            "Watchlist"
        )
