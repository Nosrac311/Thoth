from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
)


class ServiceCard(QGroupBox):

    def __init__(self, name, manager):

        super().__init__()

        self.name = name
        self.manager = manager

        self.setTitle(name)

        self.status = QLabel(
            "STOPPED"
        )

        self.restart_button = QPushButton(
            "Restart"
        )

        self.stop_button = QPushButton(
            "Stop"
        )

        buttons = QHBoxLayout()

        buttons.addWidget(
            self.restart_button
        )

        buttons.addWidget(
            self.stop_button
        )

        layout = QVBoxLayout()

        layout.addWidget(
            self.status
        )

        layout.addLayout(
            buttons
        )

        self.setLayout(
            layout
        )

        self.restart_button.clicked.connect(
            self.restart
        )

        self.stop_button.clicked.connect(
            self.stop
        )

    def refresh(self):

        state = self.manager.status().get(
            self.name,
            "STOPPED"
        )

        if state == "ONLINE":

            self.status.setText(
                "● ONLINE"
            )

            self.status.setStyleSheet(
                "color:#00ff88;font-weight:bold;"
            )

        else:

            self.status.setText(
                "● STOPPED"
            )

            self.status.setStyleSheet(
                "color:#ff5555;font-weight:bold;"
            )

    def restart(self):

        if self.name == "Discord Bot":

            self.manager.restart_bot()

        elif self.name == "FastAPI Dashboard":

            self.manager.restart_dashboard()

    def stop(self):

        if self.name == "Discord Bot":

            self.manager.stop_bot()

        elif self.name == "FastAPI Dashboard":

            self.manager.stop_dashboard()
