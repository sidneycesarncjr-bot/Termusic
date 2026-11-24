
from textual.widgets import Static
from textual.containers import Vertical


class Sidebar(Vertical):

    ITEMS = [
        "Início",
        "Biblioteca",
        "Histórico",
        "Fila",
        "Playlist",
    ]

    def __init__(self):
        super().__init__(id="sidebar")

    def compose(self):

        yield Static(
            "[bold #B5F36D]TERMUSIC[/]\n",
            id="sidebar-title"
        )

        for index, item in enumerate(self.ITEMS):
            yield Static(
                f"  {item}",
                id=f"sidebar-item-{index}",
                classes="sidebar-item"
            )

    def select(self, index):

        for i, item in enumerate(self.ITEMS):

            widget = self.query_one(
                f"#sidebar-item-{i}",
                Static
            )

            if i == index:
                widget.update(
                    f"[bold #B5F36D]> {item}[/]"
                )
            else:
                widget.update(
                    f"[#AAAAAA]  {item}[/]"
                )
