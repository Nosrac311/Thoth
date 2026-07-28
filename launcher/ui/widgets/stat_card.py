from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
)


class StatCard(QFrame):

    def __init__(self, title):

        super().__init__()

        self.setObjectName(
            "StatCard"
        )

        layout = QVBoxLayout()

        self.title = QLabel(title)

        self.value = QLabel(
            "0"
        )

        self.value.setObjectName(
            "StatValue"
        )

        layout.addWidget(
            self.title
        )

        layout.addWidget(
            self.value
        )

        self.setLayout(
            layout
        )

    def setValue(self, value):

        self.value.setText(
            str(value)
        )
