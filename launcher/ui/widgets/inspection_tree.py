from collections import defaultdict

from database.watchlist import (
    is_watched_by_any_user,
)

from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
)


class InspectionTree(QTreeWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setColumnCount(6)

        self.setHeaderLabels([
            "Restaurant",
            "Date",
            "Score",
            "Grade",
            "Inspector ID",
            "Location",
        ])

        self.setAlternatingRowColors(True)

        header = self.header()

        header.setSectionResizeMode(
            0,
            QHeaderView.Stretch,
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.Fixed,
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.Fixed,
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.Fixed,
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.Fixed,
        )

        header.setSectionResizeMode(
            5,
            QHeaderView.Stretch,
        )

        self.setColumnWidth(
            1,
            100,
        )

        self.setColumnWidth(
            2,
            80,
        )

        self.setColumnWidth(
            3,
            80,
        )

        self.setColumnWidth(
            4,
            80,
        )


    # --------------------------------------------------
    # LOAD INSPECTIONS
    # --------------------------------------------------

    def load_inspections(self, rows):

        self.clear()

        counties = defaultdict(list)


        #
        # Group inspections by county
        #

        for row in rows:

            county = row[4]

            counties[county].append(
                row
            )


        #
        # Build tree
        #

        for county, inspections in sorted(
            counties.items()
        ):

            county_item = QTreeWidgetItem([
                f"{county} ({len(inspections)})"
            ])

            self.addTopLevelItem(
                county_item
            )

            inspectors = defaultdict(list)


            #
            # Group county inspections
            # by inspector
            #

            for inspection in inspections:

                inspector_id = inspection[5]

                inspectors[
                    inspector_id
                ].append(
                    inspection
                )


            #
            # Inspector level
            #

            for (
                inspector_id,
                inspector_rows,
            ) in sorted(
                inspectors.items()
            ):

                inspector_item = QTreeWidgetItem([
                    f"Inspector {inspector_id} "
                    f"({len(inspector_rows)})"
                ])

                county_item.addChild(
                    inspector_item
                )


                #
                # Inspection level
                #

                for inspection in inspector_rows:

                    restaurant = str(
                        inspection[0]
                    )


                    #
                    # Highlight restaurant if
                    # ANY user is watching it.
                    #
                    # We do NOT retrieve a user's
                    # private watchlist here because
                    # the desktop launcher has no
                    # logged-in user.
                    #

                    if is_watched_by_any_user(
                        restaurant
                    ):

                        restaurant = (
                            "★ " + restaurant
                        )


                    inspection_item = QTreeWidgetItem([
                        restaurant,
                        str(inspection[1]),
                        str(inspection[2]),
                        str(inspection[3]),
                        str(inspection[5]),
                        str(inspection[6]),
                    ])

                    inspector_item.addChild(
                        inspection_item
                    )


            county_item.setExpanded(
                False
            )


    # --------------------------------------------------
    # FILTER TREE
    # --------------------------------------------------

    def filter_tree(self, text):

        text = text.lower().strip()


        for i in range(
            self.topLevelItemCount()
        ):

            county_item = (
                self.topLevelItem(i)
            )

            county_visible = False


            for j in range(
                county_item.childCount()
            ):

                inspector_item = (
                    county_item.child(j)
                )

                inspector_visible = False


                for k in range(
                    inspector_item.childCount()
                ):

                    inspection_item = (
                        inspector_item.child(k)
                    )

                    match = False


                    for column in range(
                        self.columnCount()
                    ):

                        if (
                            text
                            in inspection_item
                            .text(column)
                            .lower()
                        ):

                            match = True

                            break


                    inspection_item.setHidden(
                        not match
                    )


                    if match:

                        inspector_visible = True

                        inspection_item.setExpanded(
                            True
                        )


                inspector_item.setHidden(
                    not inspector_visible
                )


                if inspector_visible:

                    county_visible = True

                    inspector_item.setExpanded(
                        True
                    )


            county_item.setHidden(
                not county_visible
            )


            if county_visible:

                county_item.setExpanded(
                    True
                )


    # --------------------------------------------------
    # WATCHLIST
    # --------------------------------------------------
    #
    # The old implementation attempted to call:
    #
    #     get_watchlist()
    #
    # without a user ID.
    #
    # That is no longer valid because watchlists are
    # user-specific.
    #
    # The desktop launcher therefore does not expose
    # individual users' watchlist entries.
    #
    # The inspection tree itself already marks any
    # restaurant watched by at least one user with ★.
    #
    # Mobile users see their own private watchlist.
    # --------------------------------------------------

    def load_watchlist(self, rows):

        return


    def load_watchlist_branch(self):

        return
