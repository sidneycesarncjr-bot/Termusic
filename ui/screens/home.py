
from rich.console import Group
from rich.text import Text
from rich.rule import Rule


def get_content(music_count=0, cover_data=None):

    music_info = Group(
        Text("SUA BIBLIOTECA", style="bold #777777"),
        Text(
            f"{music_count:03d}",
            style="bold #B5F36D"
        ),
        Text("músicas encontradas", style="#888888")
    )

    return Group(
        Text("TERMUSIC", style="bold #B5F36D"),
        Text("UFAL - 2026", style="bold white"),
        Text("Alunos: a,b,c,d", style="#777777"),
        Text(""),
        Rule(style="#303030"),
        Text(""),
        music_info
    )
