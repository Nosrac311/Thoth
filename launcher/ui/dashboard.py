from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget
)

from launcher.ui.widgets.inspection_tree import InspectionTree
from launcher.ui.widgets.stat_card import StatCard
from launcher.ui.widgets.inspection_search import InspectionSearch

from database import (
    get_inspection_count,
    get_latest_inspections,
)


class DashboardWidget(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        self.title = QLabel(
            "Thoth Dashboard"
        )
        self.title.setObjectName(
            "DashboardTitle"
        )
        self.inspection_card = StatCard(
            "Total Inspections"
        )

        stats_layout = QHBoxLayout()

        stats_layout.addWidget(
            self.inspection_card
        )

        stats_layout.addStretch()

        self.search = InspectionSearch()

        self.tree = InspectionTree()

        self.expand_button = QPushButton(
            "Expand All"
        )

        self.collapse_button = QPushButton(
            "Collapse All"
        )

        button_layout = QHBoxLayout()

        button_layout.addWidget(
            self.expand_button
        )

        button_layout.addWidget(
            self.collapse_button
        )

        button_layout.addStretch()

        layout.addWidget(
            self.title
        )

        layout.addLayout(
            stats_layout
        )

        layout.addWidget(
            self.search
        )

        layout.addLayout(
            button_layout
        )

        layout.addWidget(
            self.tree
        )

        layout.setContentsMargins(
            15,
            15,
            15,
            15
        )

        layout.setSpacing(
            12
        )

        self.expand_button.clicked.connect(
            self.expand_tree
        )

        self.collapse_button.clicked.connect(
            self.collapse_tree
        )

        self.search.search_changed.connect(
            self.tree.filter_tree
        )

        self.setLayout(layout)

        self.refresh()

    def refresh(self):

        self.inspection_card.setValue(
            get_inspection_count()
        )

        rows = get_latest_inspections()

        self.tree.load_inspections(
            rows
        )

    def expand_tree(self):

        self.tree.expandAll()

    def collapse_tree(self):

        self.tree.collapseAll()
