
import asyncio
from io import BytesIO

from PIL import Image as PILImage

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Input
from textual_image.widget import Image

from ui.widgets.sidebar import Sidebar
from ui.widgets.music_player import MusicPlayer
from ui.widgets.encontrar_pasta import FolderPicker
from ui.widgets.music_list import (
    MusicList,
    MusicSelected,
    MusicQueued,
    MusicAddedToPlaylist,
)

from ui.lista_musicas import find_music_files

from ui.screens.home import get_content as home_content
from ui.screens.library import get_content as library_content
from ui.screens.history import get_content as history_content
from ui.screens.queue import get_content as queue_content
from ui.screens.playlist_screen import get_content as playlist_content

from ui.historico import HistoricoPilha
from ui.fila import Fila
from ui.playlist import ListaDuplamenteCircular
from ui.audio_player import AudioPlayer


class TermusicApp(App):

    TITLE = "Termusic"
    SUB_TITLE = "Music Player"

    PAGES = Sidebar.ITEMS

    def __init__(self):
        super().__init__()

        self.selected_index = 0
        self.current_page = "Início"
        self.music_count = 0
        self.current_cover = None
        self.current_music = None
        self.audio_player = AudioPlayer()
        self.playback_active = False
        self.play_request_id = 0
        self.repeat_mode = "all"

        # Histórico de músicas reproduzidas
        self.historico = HistoricoPilha(limite=100)
        self.fila = Fila()
        self.playlist = ListaDuplamenteCircular()
        self.playlist_selected_index = 0

    def on_mount(self):
        self.run_worker(
            self.monitor_playback(),
            name="playback-monitor",
            exclusive=True,
        )

    async def on_unmount(self):
        await asyncio.to_thread(self.audio_player.close)

    async def monitor_playback(self):
        while True:
            await asyncio.sleep(0.4)
            if not self.playback_active:
                continue
            # O resultado pode chegar depois que o usuário já mudou de faixa.
            # Associe a consulta ao carregamento que estava ativo ao iniciá-la.
            request_id = self.play_request_id
            try:
                terminou = await asyncio.to_thread(self.audio_player.is_ended)
            except Exception as error:
                if request_id != self.play_request_id:
                    continue
                self.playback_active = False
                self.notify(f"Erro ao consultar o MPV: {error}", severity="error")
                continue
            if (
                request_id == self.play_request_id
                and terminou
                and self.playback_active
            ):
                self.playback_active = False
                self._on_track_finished()

    CSS = """

    Screen {
        background: #101010;
        color: #FFFFFF;

        layout: grid;
        grid-size: 2 2;
        grid-columns: 28 1fr;
        grid-rows: 1fr 7;
    }

    #sidebar {
        row-span: 2;
        background: #151515;
        padding: 2;
        border-right: solid #292929;
    }

    #main-content {
        background: #101010;
        padding: 2 3;
    }

    #page-content {
        height: auto;
        color: #FFFFFF;
    }

    #album-cover {
        width: 30;
        height: 15;
        margin-top: 2;
    }

    #folder-tree {
        display: none;
        height: 1fr;
        background: #151515;
        border: solid #292929;
    }

    #music-search {
        display: none;
        margin-bottom: 1;
        background: #181818;
        color: #FFFFFF;
        border: solid #303030;
    }

    #music-search:focus {
        border: solid #B5F36D;
    }

    #music-list {
        display: none;
        height: 1fr;
        background: #101010;
        color: #FFFFFF;
        padding: 1;
        content-align: left top;
    }

    #music-player {
        background: #181818;
        border-top: solid #303030;
        height: 7;
        padding: 1 2;
        layout: horizontal;
        align: center middle;
    }

    #track-info {
        width: 1fr;
        content-align: left middle;
    }

    #player-controls {
        width: 30;
        content-align: center middle;
    }

    #track-progress {
        width: 1fr;
        content-align: right middle;
    }

    """

    # Montagem da interface
    def compose(self) -> ComposeResult:

        yield Sidebar()

        with Vertical(id="main-content"):

            yield Static(
                self.get_page_content("Início"),
                id="page-content"
            )

            yield Image(id="album-cover")

            yield FolderPicker()

            yield Input(
                placeholder="Pesquisar música ",
                id="music-search"
            )

            yield MusicList()

        yield MusicPlayer()

    # Conteúdo de cada página
    def get_page_content(self, page):

        if page == "Início":
            return home_content(
                self.music_count,
                self.current_cover
            )

        if page == "Biblioteca":
            return library_content()

        if page == "Histórico":
            return history_content(self.historico)

        if page == "Fila":
            return queue_content(self.fila)

        if page == "Playlist":
            return playlist_content(self.playlist, self.playlist_selected_index)

        return ""

    # Carregamento das músicas
    async def load_music(self, folder):

        music_files = await asyncio.to_thread(
            find_music_files,
            folder
        )

        if self.current_page != "Biblioteca":
            return

        music_list = self.query_one("#music-list", MusicList)

        music_list.set_musics(music_files)

        # Quantidade de músicas encontradas
        self.music_count = len(music_list.indice_titulos)

    # Navegação da sidebar
    def move_selection(self, direction):

        self.selected_index = (
            self.selected_index + direction
        ) % len(self.PAGES)

        self.query_one("#sidebar", Sidebar).select(
            self.selected_index
        )

    # Abertura das páginas
    def open_page(self):

        new_page = self.PAGES[self.selected_index]

        if new_page == self.current_page:
            return

        self.current_page = new_page

        page_content = self.query_one("#page-content", Static)
        cover_widget = self.query_one("#album-cover", Image)
        folder_tree = self.query_one("#folder-tree", FolderPicker)
        search_input = self.query_one("#music-search", Input)
        music_list = self.query_one("#music-list", MusicList)

        page_content.styles.display = "block"

        cover_widget.styles.display = (
            "block" if new_page == "Início" else "none"
        )

        folder_tree.styles.display = "none"
        search_input.styles.display = "none"
        music_list.styles.display = "none"

        page_content.update(
            self.get_page_content(new_page)
        )

        if new_page == "Biblioteca":
            folder_tree.styles.display = "block"
            folder_tree.focus()

        else:
            self.set_focus(None)

    # Seleção de pastas
    def on_folder_picker_folder_chosen(
        self,
        event: FolderPicker.FolderChosen
    ):

        folder = event.path

        folder_tree = self.query_one("#folder-tree", FolderPicker)
        search_input = self.query_one("#music-search", Input)
        music_list = self.query_one("#music-list", MusicList)
        page_content = self.query_one("#page-content", Static)
        cover_widget = self.query_one("#album-cover", Image)

        page_content.styles.display = "none"
        cover_widget.styles.display = "none"
        folder_tree.styles.display = "none"

        search_input.value = ""
        search_input.styles.display = "block"

        music_list.styles.display = "block"

        self.run_worker(
            self.load_music(folder),
            name="music-scan",
            exclusive=True
        )

        search_input.focus()

    # Pesquisa de músicas
    def on_input_changed(self, event: Input.Changed):

        if event.input.id == "music-search":

            music_list = self.query_one("#music-list", MusicList)

            music_list.filter_musics(event.value)

    # Atualização da capa e do player visual
    def on_music_selected(self, event: MusicSelected):
        no_existente = self.playlist.buscar(event.music)
        if no_existente is None:
            self.playlist.inserir_fim(event.music)
            faixa = event.music
        else:
            faixa = no_existente.dado
        self.playlist.definir_atual(faixa)
        self.selecionar_faixa(faixa)

    def on_music_queued(self, event: MusicQueued):
        self.fila.enfileirar(event.music)
        self.atualizar_fila()
        self.notify(f"Adicionada à fila: {event.music['title']}")
        if self.current_music is None:
            proxima = self.fila.desenfileirar()
            self.atualizar_fila()
            self.selecionar_faixa(proxima)

    def on_music_added_to_playlist(self, event: MusicAddedToPlaylist):
        self.playlist.inserir_fim(event.music)
        if self.current_page == "Playlist":
            self.query_one("#page-content", Static).update(
                self.get_page_content("Playlist")
            )
        self.notify(f"Adicionada à playlist: {event.music['title']}")

    def selecionar_faixa(self, music):
        self.current_music = music
        self.playback_active = False
        self.play_request_id += 1
        request_id = self.play_request_id
        self.mostrar_faixa(music)
        self.run_worker(
            self._play_track(music, request_id),
            name="play-track",
            exclusive=True,
        )

    async def _play_track(self, music, request_id):
        try:
            await asyncio.to_thread(self.audio_player.play, music.path)
        except Exception as error:
            if request_id == self.play_request_id:
                self.current_music = None
                self.playback_active = False
                self.notify(f"Não foi possível tocar a faixa: {error}", severity="error")
                self.query_one(MusicPlayer).set_playback_state(
                    False, self.repeat_mode
                )
            return

        if request_id != self.play_request_id:
            return
        self.playback_active = True
        self.registrar_musica_tocada(music)
        self.query_one(MusicPlayer).set_playback_state(
            True, self.repeat_mode
        )
        if self.current_page == "Histórico":
            self.query_one("#page-content", Static).update(
                self.get_page_content("Histórico")
            )

    def mostrar_faixa(self, music):
        self.current_cover = music.get("cover")

        cover_widget = self.query_one("#album-cover", Image)
        if self.current_cover:
            cover_widget.image = PILImage.open(BytesIO(self.current_cover))
        else:
            cover_widget.image = None

        self.query_one(MusicPlayer).set_track(music)
        self.query_one(MusicPlayer).set_playback_state(
            self.playback_active, self.repeat_mode
        )

    def atualizar_fila(self):
        if self.current_page == "Fila":
            self.query_one("#page-content", Static).update(
                self.get_page_content("Fila")
            )

    def next_track(self):
        if not self.fila.esta_vazia():
            music = self.fila.desenfileirar()
            self.atualizar_fila()
            self.selecionar_faixa(music)
            return

        if self.playlist.esta_vazia():
            self.notify("Não há próxima faixa na fila ou playlist.")
            return

        if (
            self.repeat_mode == "off"
            and self.playlist.indice_atual() == len(self.playlist) - 1
        ):
            self.notify("Você chegou ao fim da playlist.")
            return

        music = self.playlist.proxima()
        self.playlist_selected_index = self.playlist.indice_atual()
        self.selecionar_faixa(music)
        self.atualizar_playlist()

    def previous_track(self):
        if self.playlist.esta_vazia():
            self.notify("A playlist está vazia.")
            return
        if self.repeat_mode == "off" and self.playlist.indice_atual() == 0:
            self.notify("Você está no início da playlist.")
            return
        music = self.playlist.anterior()
        self.playlist_selected_index = self.playlist.indice_atual()
        self.selecionar_faixa(music)
        self.atualizar_playlist()

    def cycle_repeat_mode(self):
        modos = ("off", "one", "all")
        indice = modos.index(self.repeat_mode)
        self.repeat_mode = modos[(indice + 1) % len(modos)]
        self.notify(f"Modo de repetição: {self.repeat_mode}")
        self.query_one(MusicPlayer).set_playback_state(
            self.playback_active, self.repeat_mode
        )

    def toggle_playback(self):
        if self.current_music is None:
            self.notify("Selecione uma faixa primeiro.")
            return
        self.run_worker(
            self._toggle_playback(),
            name="toggle-playback",
            exclusive=True,
        )

    async def _toggle_playback(self):
        try:
            pausado = await asyncio.to_thread(self.audio_player.is_paused)
            if pausado:
                await asyncio.to_thread(self.audio_player.resume)
                self.playback_active = True
            else:
                await asyncio.to_thread(self.audio_player.pause)
                self.playback_active = False
        except Exception as error:
            self.notify(f"Não foi possível alterar a reprodução: {error}", severity="error")
            return
        self.query_one(MusicPlayer).set_playback_state(
            self.playback_active, self.repeat_mode
        )

    def _on_track_finished(self):
        atual = self.current_music
        if atual is None:
            return

        if self.repeat_mode == "one":
            # Recarregar o mesmo arquivo limpa o estado EOF do MPV e reinicia
            # a faixa, inclusive quando ela terminou com keep-open habilitado.
            self.selecionar_faixa(atual)
            return

        if not self.fila.esta_vazia():
            proxima = self.fila.desenfileirar()
            self.atualizar_fila()
            self.selecionar_faixa(proxima)
            return

        if self.playlist.esta_vazia():
            self.limpar_faixa_atual()
            return

        esta_na_ultima = self.playlist.indice_atual() == len(self.playlist) - 1
        if self.repeat_mode == "off" and esta_na_ultima:
            self.limpar_faixa_atual()
            return

        proxima = self.playlist.proxima()
        self.playlist_selected_index = self.playlist.indice_atual()
        self.selecionar_faixa(proxima)
        self.atualizar_playlist()

    def atualizar_playlist(self):
        self.query_one("#page-content", Static).update(
            self.get_page_content("Playlist")
        )

    def limpar_faixa_atual(self, parar_audio=False):
        self.current_music = None
        self.playback_active = False
        self.current_cover = None
        self.query_one("#album-cover", Image).image = None
        self.query_one(MusicPlayer).clear_track()
        self.query_one(MusicPlayer).set_playback_state(
            False, self.repeat_mode
        )
        if parar_audio and self.audio_player.process:
            self.run_worker(
                asyncio.to_thread(self.audio_player.stop),
                name="stop-playback",
                exclusive=True,
            )

    # Controle de teclado
    def on_key(self, event):

        folder_tree = self.query_one("#folder-tree", FolderPicker)
        search_input = self.query_one("#music-search", Input)
        music_list = self.query_one("#music-list", MusicList)
        page_content = self.query_one("#page-content", Static)
        cover_widget = self.query_one("#album-cover", Image)

        # Voltar com Backspace
        if event.key == "backspace":

            # Deixa o Input apagar o caractere
            if self.focused is search_input:
                return

            # Nível 1: lista -> árvore de pastas
            if music_list.styles.display == "block":

                search_input.styles.display = "none"
                search_input.value = ""

                music_list.styles.display = "none"
                folder_tree.styles.display = "block"

                folder_tree.focus()

                event.stop()
                return

            # Nível 2: árvore -> página da Biblioteca
            if folder_tree.styles.display == "block":

                folder_tree.styles.display = "none"

                page_content.styles.display = "block"

                cover_widget.styles.display = (
                    "block" if self.current_page == "Início" else "none"
                )

                self.set_focus(None)

                event.stop()
                return

            # Nível 3: página -> Início
            if self.current_page != "Início":

                self.current_page = "Início"
                self.selected_index = 0

                page_content.update(
                    self.get_page_content("Início")
                )

                page_content.styles.display = "block"
                cover_widget.styles.display = "block"

                folder_tree.styles.display = "none"
                search_input.styles.display = "none"
                music_list.styles.display = "none"

                self.query_one("#sidebar", Sidebar).select(0)

                self.set_focus(None)

                event.stop()
                return

            return

        # Árvore de pastas aberta
        if folder_tree.styles.display == "block":
            return

        # Biblioteca com lista aberta
        if music_list.styles.display == "block":

            # TAB alterna entre pesquisa e lista
            if event.key == "tab":

                event.stop()

                if self.focused is search_input:
                    music_list.focus()
                else:
                    search_input.focus()

                return

            # Deixa o Input tratar as teclas
            if self.focused is search_input:
                return

            # Setas e Enter são tratados pelos BINDINGS da MusicList
            return

        if self.current_page == "Playlist":
            tamanho = len(self.playlist)
            if event.key in ("left", "right") and tamanho:
                if event.key == "left":
                    self.previous_track()
                else:
                    self.next_track()
                event.stop()
                return

            if event.key in ("up", "down") and tamanho:
                delta = -1 if event.key == "up" else 1
                self.playlist_selected_index = (
                    self.playlist_selected_index + delta
                ) % tamanho
                self.atualizar_playlist()
                event.stop()
                return

            if event.key == "enter" and tamanho:
                self.playlist.definir_atual_indice(
                    self.playlist_selected_index
                )
                music = self.playlist.tocar_atual()
                self.selecionar_faixa(music)
                self.atualizar_playlist()
                event.stop()
                return

            if event.key == "delete" and tamanho:
                indice_removido = self.playlist_selected_index
                faixa_removida = self.playlist.item_no_indice(indice_removido)
                removendo_atual = (
                    self.playlist.indice_atual()
                    == indice_removido
                )
                removendo_faixa_tocada = (
                    self.current_music is not None
                    and faixa_removida is not None
                    and self.current_music.path == faixa_removida.path
                )
                self.playlist.remover_indice(indice_removido)
                if len(self.playlist):
                    self.playlist_selected_index %= len(self.playlist)
                    atual = self.playlist.tocar_atual()
                    if removendo_faixa_tocada and atual is not None:
                        self.selecionar_faixa(atual)
                    elif removendo_atual:
                        self.atualizar_playlist()
                else:
                    self.playlist_selected_index = 0
                    if removendo_faixa_tocada:
                        self.limpar_faixa_atual(parar_audio=True)
                self.atualizar_playlist()
                event.stop()
                return

            if event.key in ("up", "down", "left", "right", "enter", "delete"):
                event.stop()
                return

        # Navegação da sidebar
        if event.key == "space":
            event.stop()
            self.toggle_playback()
            return
        if event.key == "n":
            event.stop()
            self.next_track()
            return
        if event.key == "b":
            event.stop()
            self.previous_track()
            return
        if event.key == "r":
            event.stop()
            self.cycle_repeat_mode()
            return

        if event.key == "up":
            event.stop()
            self.move_selection(-1)

        elif event.key == "down":
            event.stop()
            self.move_selection(1)

        elif event.key == "enter":
            event.stop()
            self.open_page()

    # Registro de músicas reproduzidas no histórico
    def registrar_musica_tocada(self, music):
        self.historico.push(music)
