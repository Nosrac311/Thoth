from collections import defaultdict
from prediction import predict_inspection
from database.stats import inspection_dates
from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView
)


class WatchlistTree(QTreeWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setColumnCount(5)

        self.setHeaderLabels([
            "Restaurant",
            "Date",
            "Score",
            "Grade",
            "Inspector ID"
        ])

        self.setAlternatingRowColors(True)

        header = self.header()

        header.setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

    def load_watchlist(self, rows):

        self.clear()

        restaurants = defaultdict(list)

        for row in rows:

            restaurant = row[0]

            dates = inspection_dates(
                restaurant
            )

            restaurants[restaurant].append(row)

        for restaurant, inspections in sorted(restaurants.items()):

            for inspection in inspections:

                restaurant_item = QTreeWidgetItem([
                    str(inspection[0]),  # Restaurant
                    str(inspection[1]),  # Date
                    str(inspection[2]),  # Score
                    str(inspection[3]),  # Grade
                    str(inspection[4]),  # Inspector ID
                ])

                self.addTopLevelItem(
                    restaurant_item
                )

                # Empty placeholder child
                prediction = predict_inspection(
                    inspection[4],   # inspector id
                    inspection[3],   # grade
                    inspection[1],   # date
                    dates
                )

                blank_item = QTreeWidgetItem([
                    "Prediction",
                    prediction["window"],
                    f"{prediction['confidence']}%",
                    "",
                    ""
                ])

                restaurant_item.addChild(
                    blank_item
                )

                restaurant_item.setExpanded(
                    False
                )
