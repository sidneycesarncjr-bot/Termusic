from rich.console import Group
from rich.markup import escape
from rich.table import Table
from rich.text import Text


def get_content(musics=()):
    if len(musics) == 0:
        return Group(
            Text("TOCAR A SEGUIR", style="bold #B5F36D"),
            Text(""),
            Text("A fila está vazia.", style="#888888"),
            Text("Na Biblioteca, pressione Q sobre uma música para adicioná-la.", style="#777777"),
        )

    table = Table(
        expand=True,
        box=None,
        show_header=True,
        padding=(0, 1),
        header_style="#777777",
    )
    table.add_column("#", justify="right", width=4)
    table.add_column("TÍTULO", ratio=5)
    table.add_column("ARTISTA", ratio=3)
    table.add_column("DURAÇÃO", justify="right", width=10)

    for position, music in enumerate(musics, start=1):
        table.add_row(
            str(position),
            escape(music.get("title", "Faixa desconhecida")),
            escape(music.get("artist", "Artista desconhecido")),
            escape(music.get("duration", "--:--")),
        )

    return Group(
        Text("TOCAR A SEGUIR", style="bold #B5F36D"),
        Text("As faixas serão tocadas na ordem em que foram adicionadas.", style="#888888"),
        Text(""),
        table,
    )
