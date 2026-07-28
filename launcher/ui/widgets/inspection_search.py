from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)

from PySide6.QtCore import Signal


class InspectionSearch(QWidget):

    search_changed = Signal(str)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.search_box = QLineEdit()

        self.search_box.setPlaceholderText(
            "Search inspections..."
        )

        self.clear_button = QPushButton(
            "Clear"
        )

        layout = QHBoxLayout()

        layout.addWidget(
            self.search_box
        )

        layout.addWidget(
            self.clear_button
        )

        self.setLayout(
            layout
        )

        self.search_box.textChanged.connect(
            self.search_changed.emit
        )

        self.clear_button.clicked.connect(
            self.clear
        )

    def clear(self):

        self.search_box.clear()
