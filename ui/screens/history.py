from rich.console import Group
from rich.table import Table
from rich.text import Text


def get_content(musics=()):
    """Monta a tela com as músicas selecionadas mais recentemente primeiro."""
    items = list(musics)
    if not items:
        return Group(
            Text("HISTÓRICO", style="bold #B5F36D"),
            Text(""),
            Text("Nenhuma música reproduzida ainda.", style="#888888"),
            Text("Selecione uma música na Biblioteca para vê-la aqui.", style="#777777"),
        )

    table = Table(
        expand=True,
        box=None,
        show_header=True,
        padding=(0, 1),
        header_style="#777777",
    )
    table.add_column("TÍTULO", ratio=5)
    table.add_column("ARTISTA", ratio=3)
    table.add_column("DURAÇÃO", justify="right", width=10)

    for music in items:
        table.add_row(
            music.get("title", "Faixa desconhecida"),
            music.get("artist", "Artista desconhecido"),
            music.get("duration", "--:--"),
        )

    return Group(
        Text("HISTÓRICO", style="bold #B5F36D"),
        Text("Suas músicas recentes", style="#888888"),
        Text(""),
        table,
    )
