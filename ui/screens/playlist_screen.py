from rich.console import Group
from rich.markup import escape
from rich.table import Table
from rich.text import Text


def get_content(playlist, selected_index=0):
    items = list(playlist)
    if not items:
        return Group(
            Text("PLAYLIST", style="bold #B5F36D"),
            Text(""),
            Text("Sua playlist está vazia.", style="#888888"),
            Text("Na Biblioteca, pressione P sobre uma música para adicioná-la.", style="#777777"),
        )

    table = Table(
        expand=True,
        box=None,
        show_header=True,
        padding=(0, 1),
        header_style="#777777",
    )
    table.add_column("", width=3)
    table.add_column("TÍTULO", ratio=5)
    table.add_column("ARTISTA", ratio=3)
    table.add_column("DURAÇÃO", justify="right", width=10)

    atual_index = playlist.indice_atual()

    for index, music in enumerate(items):
        marker = "▶" if index == atual_index else " "
        style = "bold #B5F36D" if index == selected_index else "#FFFFFF"
        table.add_row(
            marker,
            escape(music.get("title", "Faixa desconhecida")),
            escape(music.get("artist", "Artista desconhecido")),
            escape(music.get("duration", "--:--")),
            style=style,
        )

    return Group(
        Text("PLAYLIST", style="bold #B5F36D"),
        Text("↑/↓ escolher  •  Enter selecionar  •  ←/→ faixa anterior/próxima  •  Delete remover", style="#888888"),
        Text(""),
        table,
    )
