from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QTextEdit,
    QPushButton,
    QLineEdit,
    QLabel,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QMenu,
    QMessageBox,
    QInputDialog
)
from PySide6.QtCore import Qt

from database import (
    get_channels,
    get_messages,
    create_message,
    create_channel,
    rename_channel,
    delete_channel
)


class ChannelsWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.current_channel = None

        main_layout = QHBoxLayout()

        # CHANNEL LIST

        left = QVBoxLayout()

        left.addWidget(
            QLabel("Channels")
        )

        self.channel_list = QListWidget()

        left.addWidget(
            self.channel_list
        )
        self.create_button = QPushButton(
            "Create Channel"
        )

        left.addWidget(
            self.create_button
        )

        self.create_button.clicked.connect(
            self.create_channel_dialog
        )

        self.channel_list.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.channel_list.customContextMenuRequested.connect(
            self.channel_menu
        )

        # MESSAGE AREA

        right = QVBoxLayout()

        self.title = QLabel(
            "Select a channel"
        )

        right.addWidget(
            self.title
        )

        self.messages = QTextEdit()

        self.messages.setReadOnly(
            True
        )

        right.addWidget(
            self.messages
        )

        # INPUT

        input_bar = QHBoxLayout()

        self.input = QLineEdit()

        self.send = QPushButton(
            "Send"
        )

        input_bar.addWidget(
            self.input
        )

        input_bar.addWidget(
            self.send
        )

        right.addLayout(
            input_bar
        )

        main_layout.addLayout(
            left,
            1
        )

        main_layout.addLayout(
            right,
            3
        )

        self.setLayout(
            main_layout
        )

        self.channel_list.itemClicked.connect(
            self.select_channel
        )

        self.send.clicked.connect(
            self.send_message
        )

        self.load_channels()

    def load_channels(self):

        self.channel_list.clear()

        channels = get_channels()

        for channel in channels:

            item = self.channel_list.addItem(
                channel[1]
            )

            # store database id
            self.channel_list.item(
                self.channel_list.count()-1
            ).setData(
                256,
                channel[0]
            )

    def select_channel(self, item):

        self.current_channel = item.data(
            256
        )

        self.title.setText(
            item.text()
        )

        self.load_messages()

    def load_messages(self):

        if not self.current_channel:
            return

        self.messages.clear()

        messages = get_messages(
            self.current_channel
        )

        for msg in messages:

            self.messages.append(
                f"[{msg[2]}] {msg[0]}: {msg[1]}"
            )

    def send_message(self):

        if not self.current_channel:
            return

        text = self.input.text().strip()

        if not text:
            return

        create_message(
            self.current_channel,
            "User",
            text
        )

        self.input.clear()

        self.load_messages()

    def create_channel_dialog(self):

        dialog = QDialog(
            self
        )

        dialog.setWindowTitle(
            "Create Channel"
        )

        layout = QFormLayout(
            dialog
        )

        name_input = QLineEdit()

        description_input = QLineEdit()

        layout.addRow(
            "Name:",
            name_input
        )

        layout.addRow(
            "Description:",
            description_input
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        layout.addWidget(
            buttons
        )

        buttons.accepted.connect(
            dialog.accept
        )

        buttons.rejected.connect(
            dialog.reject
        )

        if dialog.exec():

            name = name_input.text().strip()

            description = description_input.text().strip()

            if name:

                create_channel(
                    name,
                    description
                )

                self.load_channels()

    def channel_menu(self, position):

        item = self.channel_list.itemAt(
            position
        )

        if not item:
            return

        channel_id = item.data(
            256
        )

        menu = QMenu(
            self
        )

        rename_action = menu.addAction(
            "Rename Channel"
        )

        delete_action = menu.addAction(
            "Delete Channel"
        )

        action = menu.exec(
            self.channel_list.mapToGlobal(position)
        )

        if action == rename_action:

            self.rename_channel(
                channel_id
            )

        elif action == delete_action:

            self.delete_channel(
                channel_id
            )

    def rename_channel(self, channel_id):

        new_name, ok = QInputDialog.getText(
            self,
            "Rename Channel",
            "New name:"
        )

        if ok and new_name.strip():

            rename_channel(
                channel_id,
                new_name.strip()
            )

            self.load_channels()

    def delete_channel(self, channel_id):

        result = QMessageBox.question(
            self,
            "Delete Channel",
            "Delete this channel and all messages?"
        )

        if result == QMessageBox.Yes:

            delete_channel(
                channel_id
            )

            self.current_channel = None

            self.messages.clear()

            self.load_channels()
