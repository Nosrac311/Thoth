from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
)

from launcher.ui.widgets.service_card import ServiceCard


class StatusPanel(QWidget):

    def __init__(self, manager):

        super().__init__()

        self.manager = manager

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout()

        self.discord_card = ServiceCard(
            "Discord Bot",
            self.manager
        )

        self.dashboard_card = ServiceCard(
            "FastAPI Dashboard",
            self.manager
        )

        self.cards = [
            self.discord_card,
            self.dashboard_card,
        ]

        self.start_button = QPushButton(
            "Start All"
        )

        self.stop_button = QPushButton(
            "Stop All"
        )

        self.start_button.clicked.connect(
            self.manager.start_services
        )

        self.stop_button.clicked.connect(
            self.manager.stop_all
        )

        layout.addWidget(
            self.discord_card
        )

        layout.addWidget(
            self.dashboard_card
        )

        layout.addStretch()

        layout.addWidget(
            self.start_button
        )

        layout.addWidget(
            self.stop_button
        )

        self.setLayout(layout)

    def refresh(self):

        for card in self.cards:
            card.refresh()
