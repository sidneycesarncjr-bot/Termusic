
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
            "[#AAAAAA]B: anterior  SPACE: pausar/tocar  N: próxima[/]",
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

    def clear_track(self):
        self.query_one("#track-info", Static).update(
            "[bold #FFFFFF]Nenhuma música selecionada[/]\n"
            "[#888888]Artista desconhecido[/]"
        )
        self.query_one("#track-progress", Static).update(
            "[#888888]━━━━━━━━━━━━━━━━━━━━━━━━[/]\n"
            "[#AAAAAA]00:00                         00:00[/]"
        )

    def set_playback_state(self, playing, repeat_mode):
        status = "pausar" if playing else "tocar"
        if repeat_mode == "off":
            repetir = "desligada"
        elif repeat_mode == "one":
            repetir = "faixa"
        else:
            repetir = "playlist"
        controls = self.query_one("#player-controls", Static)
        controls.update(
            f"[#AAAAAA]B: anterior  SPACE: {status}  N: próxima  R: repetir {repetir}[/]"
        )
