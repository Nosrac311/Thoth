from collections import defaultdict
from database.watchlist import is_watched
from database.watchlist import get_watchlist

from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,

)


class InspectionTree(QTreeWidget):

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
        header.setSectionResizeMode(
            1,
            QHeaderView.Fixed
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.Fixed
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.Fixed
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.Fixed
        )

        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 80)
        self.setColumnWidth(3, 80)
        self.setColumnWidth(4, 80)

    def load_inspections(self, rows):

        self.clear()

        counties = defaultdict(list)

        #
        # Group inspections by county
        #
        for row in rows:

            county = row[4]

            counties[county].append(row)

        #
        # Build tree
        #
        for county, inspections in sorted(counties.items()):

            county_item = QTreeWidgetItem([
                f"{county} ({len(inspections)})"
            ])

            self.addTopLevelItem(
                county_item
            )

            inspectors = defaultdict(list)

            #
            # Group county inspections by inspector
            #
            for inspection in inspections:

                inspector_id = inspection[5]

                inspectors[inspector_id].append(
                    inspection
                )

            #
            # Inspector level
            #
            for inspector_id, inspector_rows in sorted(inspectors.items()):

                inspector_item = QTreeWidgetItem([
                    f"Inspector {inspector_id} ({len(inspector_rows)})"
                ])

                county_item.addChild(
                    inspector_item
                )

                #
                # Inspection level
                #
                for inspection in inspector_rows:

                    restaurant = str(inspection[0])

                    if is_watched(restaurant):

                        restaurant = "★ " + restaurant

                    inspection_item = QTreeWidgetItem([
                        restaurant,  # Restaurant
                        str(inspection[1]),  # Date
                        str(inspection[2]),  # Score
                        str(inspection[3]),  # Grade
                        str(inspection[5]),  # Inspector ID
                    ])

                    inspector_item.addChild(
                        inspection_item
                    )

            county_item.setExpanded(
                False
            )

    def filter_tree(self, text):

        text = text.lower().strip()

        for i in range(self.topLevelItemCount()):

            county_item = self.topLevelItem(i)

            county_visible = False

            for j in range(county_item.childCount()):

                inspector_item = county_item.child(j)

                inspector_visible = False

                for k in range(inspector_item.childCount()):

                    inspection_item = inspector_item.child(k)

                    match = False

                    for column in range(self.columnCount()):

                        if text in inspection_item.text(column).lower():

                            match = True
                            break

                    inspection_item.setHidden(
                        not match
                    )

                    if match:
                        inspector_visible = True

                        # Open the matching inspection
                        inspection_item.setExpanded(
                            True
                        )

                inspector_item.setHidden(
                    not inspector_visible
                )

                if inspector_visible:

                    county_visible = True

                    # Open inspector branch
                    inspector_item.setExpanded(
                        True
                    )

            county_item.setHidden(
                not county_visible
            )

            if county_visible:

                # Open county branch
                county_item.setExpanded(
                    True
                )

    def load_watchlist(self, rows):

        keywords = get_watchlist()

        if not keywords:
            return

        watch_root = QTreeWidgetItem([
            "★ WATCHLIST"
        ])

        self.addTopLevelItem(
            watch_root
        )

        matches = []

        for row in rows:

            restaurant = str(row[0]).upper()

            for keyword in keywords:

                if keyword in restaurant:

                    matches.append(row)

                    break

        for row in matches:

            restaurant_item = QTreeWidgetItem([
                str(row[0]),
                str(row[1]),
                str(row[2]),
                str(row[3]),
                str(row[5]),
            ])

            watch_root.addChild(
                restaurant_item
            )

        watch_root.setExpanded(
            True
        )

    def load_watchlist_branch(self):

        watch_root = QTreeWidgetItem([
            "★ WATCHLIST"
        ])

        self.addTopLevelItem(
            watch_root
        )

        restaurants = get_watchlist()

        for restaurant in restaurants:

            restaurant_item = QTreeWidgetItem([
                restaurant
            ])

            watch_root.addChild(
                restaurant_item
            )

        watch_root.setExpanded(
            False
        )
