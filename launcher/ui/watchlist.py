from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QInputDialog,
    QMessageBox,
)
from database import get_watchlist_matches
from launcher.ui.widgets.watchlist_tree import WatchlistTree
from database.watchlist import (
    get_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
)


class WatchlistWidget(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        self.title = QLabel(
            "Inspection Watch Keywords"
        )

        self.list = QListWidget()

        self.add_button = QPushButton(
            "Add Keyword"
        )

        self.remove_button = QPushButton(
            "Remove Selected"
        )

        self.tree = WatchlistTree()

        buttons = QHBoxLayout()

        buttons.addWidget(
            self.add_button
        )

        buttons.addWidget(
            self.remove_button
        )

        layout.addWidget(
            self.title
        )

        layout.addWidget(
            self.list
        )

        layout.addWidget(
            self.tree
        )

        layout.addLayout(
            buttons
        )

        self.setLayout(
            layout
        )

        self.add_button.clicked.connect(
            self.add_keyword
        )

        self.remove_button.clicked.connect(
            self.remove_keyword
        )

        self.refresh()

    def refresh(self):

        self.list.clear()

        for keyword in get_watchlist():

            self.list.addItem(
                keyword
            )

        matches = get_watchlist_matches()

        self.tree.load_watchlist(
            matches
        )

    def add_keyword(self):

        keyword, ok = QInputDialog.getText(
            self,
            "Add Watch Keyword",
            "Keyword:"
        )

        if ok and keyword.strip():

            add_to_watchlist(
                keyword.strip()
            )

            self.refresh()

    def remove_keyword(self):

        item = self.list.currentItem()

        if not item:
            return

        keyword = item.text()

        result = QMessageBox.question(
            self,
            "Remove Keyword",
            f"Remove '{keyword}' from watchlist?"
        )

        if result == QMessageBox.Yes:

            remove_from_watchlist(
                keyword
            )

            self.refresh()
