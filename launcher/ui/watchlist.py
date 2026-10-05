from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
)

from database import get_watchlist_matches

from launcher.ui.widgets.watchlist_tree import (
    WatchlistTree,
)

from database.watchlist import (
    get_all_watchlist_keywords,
)


class WatchlistWidget(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()


        # --------------------------------------------------
        # TITLE
        # --------------------------------------------------

        self.title = QLabel(
            "Inspection Watch Keywords"
        )


        # --------------------------------------------------
        # WATCHLIST
        # --------------------------------------------------

        self.list = QListWidget()


        # --------------------------------------------------
        # MATCHES
        # --------------------------------------------------

        self.tree = WatchlistTree()


        layout.addWidget(
            self.title
        )

        layout.addWidget(
            QLabel(
                "Keywords currently watched by users"
            )
        )

        layout.addWidget(
            self.list
        )

        layout.addWidget(
            self.tree
        )


        self.setLayout(
            layout
        )


        self.refresh()


    # --------------------------------------------------
    # REFRESH
    # --------------------------------------------------

    def refresh(self):

        self.list.clear()


        # --------------------------------------------------
        # Get keywords from ALL users.
        #
        # The launcher does not have a logged-in user,
        # so it cannot call:
        #
        #     get_watchlist(user_id)
        #
        # We intentionally do not expose ownership here.
        # --------------------------------------------------

        keywords = get_all_watchlist_keywords()


        for keyword in keywords:

            self.list.addItem(
                keyword
            )


        # --------------------------------------------------
        # Load matching inspections
        # --------------------------------------------------

        matches = get_watchlist_matches()


        self.tree.load_watchlist(
            matches
        )
