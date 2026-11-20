
from pathlib import Path

from textual.widgets import DirectoryTree
from textual.binding import Binding
from textual.message import Message


class FolderPicker(DirectoryTree):

    BINDINGS = [
        Binding("s", "select_folder", "Escolher pasta"),
    ]

    class FolderChosen(Message):

        def __init__(self, path: Path):
            super().__init__()
            self.path = path

    def __init__(self):
        super().__init__(
            Path.home(),
            id="folder-tree"
        )

    def action_select_folder(self):

        node = self.cursor_node

        if node is None or node.data is None:
            return

        path = node.data.path

        if path.is_dir():
            self.post_message(
                self.FolderChosen(path)
            )
