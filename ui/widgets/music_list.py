
from pathlib import Path

from mutagen import File as MutagenFile
from rich.table import Table
from textual.widgets import Static
from textual.binding import Binding
from textual.message import Message

from ui.historico import normalizar


class MusicSelected(Message):

    def __init__(self, music):
        super().__init__()
        self.music = music


class MusicQueued(Message):
    def __init__(self, music):
        super().__init__()
        self.music = music


class MusicAddedToPlaylist(Message):
    def __init__(self, music):
        super().__init__()
        self.music = music


class MusicList(Static):

    can_focus = True

    BINDINGS = [
        Binding("up", "move_up", "Anterior", show=False),
        Binding("down", "move_down", "Próxima", show=False),
        Binding("enter", "select_music", "Selecionar", show=False),
        Binding("q", "queue_music", "Adicionar à fila", show=False),
        Binding("p", "add_to_playlist", "Adicionar à playlist", show=False),
    ]

    def __init__(self):
        super().__init__(id="music-list")

        self.selected_index = 0
        self.musics = []
        self.filtered_musics = []

        self.update_list()

    def focus_list(self):
        self.focus()

    def read_metadata(self, path):

        try:
            audio = MutagenFile(path, easy=True)

            if audio is None:
                raise ValueError("Formato não reconhecido")

            title = audio.get(
                "title",
                [Path(path).stem]
            )[0]

            artist = audio.get(
                "artist",
                ["Artista desconhecido"]
            )[0]

            duration_seconds = int(audio.info.length)

            minutes = duration_seconds // 60
            seconds = duration_seconds % 60

            duration = f"{minutes:02d}:{seconds:02d}"

            return {
                "title": title,
                "artist": artist,
                "duration": duration,
                "path": str(path),
                "cover": self.read_cover(path)
            }

        except Exception:
            return {
                "title": Path(path).stem,
                "artist": "Artista desconhecido",
                "duration": "--:--",
                "path": str(path),
                "cover": None
            }

    def read_cover(self, path):

        try:
            audio = MutagenFile(path)

            if audio is None:
                return None

            # MP3
            if hasattr(audio, "tags") and audio.tags:
                if hasattr(audio.tags, "getall"):
                    pictures = audio.tags.getall("APIC")

                    if pictures:
                        return pictures[0].data

                # M4A / MP4
                if "covr" in audio.tags:
                    return bytes(audio.tags["covr"][0])

            # FLAC
            if hasattr(audio, "pictures") and audio.pictures:
                return audio.pictures[0].data

        except Exception:
            pass

        return None

    def filter_musics(self, search):

        search = normalizar(search)

        if not search:
            self.filtered_musics = self.musics[:]

        else:
            self.filtered_musics = [
                music
                for music in self.musics
                if search in normalizar(music["title"])
                or search in normalizar(music["artist"])
            ]

        self.selected_index = 0
        self.update_list()

    def update_list(self):

        if not self.filtered_musics:
            self.update(
                "[#777777]Nenhuma música encontrada.[/]"
            )
            return

        table = Table(
            expand=True,
            box=None,
            show_header=True,
            padding=(0, 1),
            header_style="#777777"
        )

        table.add_column("TÍTULO", ratio=5)
        table.add_column("ARTISTA", ratio=3)
        table.add_column(
            "DURAÇÃO",
            justify="right",
            width=10
        )

        for index, music in enumerate(self.filtered_musics):

            title = music["title"]
            artist = music["artist"]
            duration = music["duration"]

            if index == self.selected_index:
                style = "bold #B5F36D"
                title = f"▸ {title}"

            else:
                style = "#FFFFFF"
                title = f"  {title}"

            table.add_row(
                title,
                artist,
                duration,
                style=style
            )

        self.update(table)

    def set_musics(self, music_files):

        self.musics = [
            self.read_metadata(path)
            for path in music_files
        ]

        self.filtered_musics = self.musics[:]

        self.selected_index = 0
        self.update_list()

    def action_move_up(self):

        if not self.filtered_musics:
            return

        self.selected_index = (
            self.selected_index - 1
        ) % len(self.filtered_musics)

        self.update_list()

    def action_move_down(self):

        if not self.filtered_musics:
            return

        self.selected_index = (
            self.selected_index + 1
        ) % len(self.filtered_musics)

        self.update_list()

    def action_select_music(self):

        if not self.filtered_musics:
            return

        music = self.filtered_musics[self.selected_index]

        self.post_message(
            MusicSelected(music)
        )

    def action_queue_music(self):
        if not self.filtered_musics:
            return
        self.post_message(MusicQueued(self.filtered_musics[self.selected_index]))

    def action_add_to_playlist(self):
        if not self.filtered_musics:
            return
        self.post_message(
            MusicAddedToPlaylist(self.filtered_musics[self.selected_index])
        )
