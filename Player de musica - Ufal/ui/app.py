
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
from ui.widgets.music_list import MusicList, MusicSelected

from ui.lista_musicas import find_music_files

from ui.screens.home import get_content as home_content
from ui.screens.library import get_content as library_content


class TermusicApp(App):

    TITLE = "Termusic"
    SUB_TITLE = "Music Player"

    PAGES = Sidebar.ITEMS

    def __init__(self):
        super().__init__()
        

        self.selected_index = 0
        self.current_page = "Início"
        self.page_history = []
        self.music_count = 0
        self.current_cover = None

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

    def get_page_content(self, page):

        if page == "Início":
            return home_content(
                self.music_count,
                self.current_cover
            )

        if page == "Biblioteca":
            return library_content()

    async def load_music(self, folder):

        music_files = await asyncio.to_thread(
            find_music_files,
            folder
        )

        if self.current_page != "Biblioteca":
            return

        music_list = self.query_one("#music-list", MusicList)

        music_list.set_musics(music_files)

        self.music_count = len(music_list.musics)

    def move_selection(self, direction):

        self.selected_index = (
            self.selected_index + direction
        ) % len(self.PAGES)

        self.query_one("#sidebar", Sidebar).select(
            self.selected_index
        )

    def open_page(self):

        new_page = self.PAGES[self.selected_index]

        if new_page == self.current_page:
            return

        self.page_history.append(self.current_page)
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

    def on_input_changed(self, event: Input.Changed):

        if event.input.id == "music-search":

            music_list = self.query_one("#music-list", MusicList)

            music_list.filter_musics(event.value)

    def on_music_selected(self, event: MusicSelected):

        self.current_cover = event.music.get("cover")

        cover_widget = self.query_one("#album-cover", Image)

        if self.current_cover:
            cover_widget.image = PILImage.open(
                BytesIO(self.current_cover)
            )
        else:
            cover_widget.image = None

        player = self.query_one(MusicPlayer)
        player.set_track(event.music)

    def on_key(self, event):

        folder_tree = self.query_one("#folder-tree", FolderPicker)
        search_input = self.query_one("#music-search", Input)
        music_list = self.query_one("#music-list", MusicList)
        page_content = self.query_one("#page-content", Static)
        cover_widget = self.query_one("#album-cover", Image)

        # voltar com backspcace
        if event.key == "backspace":

            
            # deixa o Input apagar o caractere.
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

            # TAB: alternar entre pesquisa e lista
            if event.key == "tab":

                event.stop()

                if self.focused is search_input:
                    music_list.focus()
                else:
                    search_input.focus()

                return

            # Se a pesquisa estiver focada,
            # deixa o Input tratar as teclas.
            if self.focused is search_input:
                return

            # Setas e Enter são tratados pelos
            # BINDINGS da classe MusicList.
            return

        # Navegação da sidebar
        if event.key == "up":
            event.stop()
            self.move_selection(-1)

        elif event.key == "down":
            event.stop()
            self.move_selection(1)

        elif event.key == "enter":
            event.stop()
            self.open_page()

    def action_help_quit(self) -> None:
        pass
