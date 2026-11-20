
from rich.markup import escape
from textual.widgets import Static


class MusicPlayer(Static):

    def __init__(self):
        super().__init__(id="music-player")

    def compose(self):

        yield Static(
            "[bold #FFFFFF]Nenhuma música selecionada[/]\n"
            "[#888888]Artista desconhecido[/]",
            id="track-info"
        )

        yield Static(
            "[#AAAAAA]◀    [bold #B5F36D]▶[/]    ▶▶",
            id="player-controls"
        )

        yield Static(
            "[#888888]━━━━━━━━━━━━━━━━━━━━━━━━[/]\n"
            "[#AAAAAA]00:00                         00:00[/]",
            id="track-progress"
        )

    def set_track(self, music):

        title = escape(music["title"])
        artist = escape(music["artist"])
        duration = music["duration"]

        track_info = self.query_one("#track-info", Static)
        track_progress = self.query_one("#track-progress", Static)

        track_info.update(
            f"[bold #FFFFFF]{title}[/]\n"
            f"[#888888]{artist}[/]"
        )

        track_progress.update(
            "[#888888]━━━━━━━━━━━━━━━━━━━━━━━━[/]\n"
            f"[#AAAAAA]00:00                         {duration}[/]"
        )
