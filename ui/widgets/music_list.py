
from pathlib import Path

from mutagen import File as MutagenFile
from rich.console import Group
from rich.table import Table
from rich.text import Text
from textual.widgets import Static
from textual.binding import Binding
from textual.message import Message

from ui.faixa import Faixa
from ui.arvore_avl import ArvoreAVL
from ui.lista_encadeada import ListaEncadeada
from ui.tabela_hash import TabelaHash
from ui.text_utils import normalizar


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
        Binding("o", "toggle_sort_order", "Alternar ordenação AVL", show=False),
        Binding("space", "toggle_playback", "Pausar/tocar", show=False),
        Binding("n", "next_track", "Próxima faixa", show=False),
        Binding("b", "previous_track", "Faixa anterior", show=False),
        Binding("r", "cycle_repeat", "Alternar repetição", show=False),
    ]

    def __init__(self):
        super().__init__(id="music-list")

        self.selected_index = 0
        self.filtered_musics = ListaEncadeada()
        self.indice_titulos = TabelaHash()
        self.arvore_titulos = ArvoreAVL("titulo")
        self.arvore_duracoes = ArvoreAVL("duracao")
        self.criterio_ordenacao = "titulo"
        self.termo_pesquisa = ""

        self.update_list()

    def read_metadata(self, path):

        try:
            audio = MutagenFile(path, easy=True)

            if audio is None:
                raise ValueError("Formato não reconhecido")

            titles = audio.get("title")
            title = titles[0] if titles else Path(path).stem

            artists = audio.get("artist")
            artist = artists[0] if artists else "Artista desconhecido"

            duration_seconds = int(audio.info.length)

            return Faixa(
                title,
                artist,
                duration_seconds,
                str(path),
                self.read_cover(path),
            )

        except Exception:
            return Faixa(
                Path(path).stem,
                "Artista desconhecido",
                None,
                str(path),
            )

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

        self.termo_pesquisa = search
        search = normalizar(search)
        self.filtered_musics = ListaEncadeada()
        arvore = self._arvore_atual()

        if not search:
            for music in arvore.listar():
                self.filtered_musics.inserir_fim(music)

        else:
            # A hash atende buscas exatas por título, inclusive títulos repetidos.
            for music in self.indice_titulos.buscar(search):
                self.filtered_musics.inserir_fim(music)

            # Mantém a pesquisa parcial por título e artista como alternativa.
            if self.filtered_musics.esta_vazia():
                for music in arvore.listar():
                    if (
                        search in normalizar(music["title"])
                        or search in normalizar(music["artist"])
                    ):
                        self.filtered_musics.inserir_fim(music)

        self.selected_index = 0
        self.update_list()

    def _arvore_atual(self):
        if self.criterio_ordenacao == "duracao":
            return self.arvore_duracoes
        return self.arvore_titulos

    def action_toggle_sort_order(self):
        self.criterio_ordenacao = (
            "duracao" if self.criterio_ordenacao == "titulo" else "titulo"
        )
        self.filter_musics(self.termo_pesquisa)

    def update_list(self):

        if not self.filtered_musics:
            self.update(
                Group(
                    Text(self._texto_ordenacao(), style="#777777"),
                    Text("Nenhuma música encontrada.", style="#777777"),
                )
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

        self.update(
            Group(
                Text(self._texto_ordenacao(), style="#777777"),
                table,
            )
        )

    def _texto_ordenacao(self):
        criterio = "título" if self.criterio_ordenacao == "titulo" else "duração"
        return (
            f"AVL por {criterio} • ENTER tocar • Q fila • P playlist • "
            "N/B próxima/anterior • R repetição • TAB+O ordenar"
        )

    def set_musics(self, music_files):

        self.filtered_musics = ListaEncadeada()
        self.indice_titulos = TabelaHash()
        self.arvore_titulos = ArvoreAVL("titulo")
        self.arvore_duracoes = ArvoreAVL("duracao")
        self.termo_pesquisa = ""

        for path in music_files:
            music = self.read_metadata(path)
            self.indice_titulos.inserir(music)
            self.arvore_titulos.inserir(music)
            self.arvore_duracoes.inserir(music)

        for music in self._arvore_atual().listar():
            self.filtered_musics.inserir_fim(music)

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

    def action_toggle_playback(self):
        self.app.toggle_playback()

    def action_next_track(self):
        self.app.next_track()

    def action_previous_track(self):
        self.app.previous_track()

    def action_cycle_repeat(self):
        self.app.cycle_repeat_mode()
