from collections import defaultdict

from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
)


class InspectorTree(QTreeWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setColumnCount(5)

        self.setHeaderLabels([
            "Restaurant",
            "Date",
            "Score",
            "Grade",
            "County"
        ])

        self.setAlternatingRowColors(True)

    def load_inspections(self, rows):

        self.clear()

        inspectors = defaultdict(list)

        for row in rows:

            inspector_id = row[5]

            inspectors[inspector_id].append(row)

        for inspector_id in sorted(inspectors):

            inspector_item = QTreeWidgetItem([
                f"Inspector {inspector_id} ({len(inspectors[inspector_id])})"
            ])

            self.addTopLevelItem(
                inspector_item
            )

            for inspection in inspectors[inspector_id]:

                child = QTreeWidgetItem([
                    inspection[0],       # Restaurant
                    str(inspection[1]),  # Date
                    str(inspection[2]),  # Score
                    inspection[3],       # Grade
                    inspection[4],       # County
                ])

                inspector_item.addChild(
                    child
                )

            inspector_item.setExpanded(
                False
            )
