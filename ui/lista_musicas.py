
import os
from pathlib import Path

from ui.lista_encadeada import ListaEncadeada

AUDIO_EXTENSIONS = (
    ".mp3",
    ".wav",
    ".flac",
    ".aac",
    ".ogg",
    ".opus",
    ".wma",
    ".m4a",
    ".aiff",
    ".aif",
    ".alac",
    ".ape",
    ".mid",
    ".midi",
    ".amr",
    ".ac3",
    ".mp2",
    ".au",
)

#procura se tem musicas ou não no diretorio. se tiver ele mostra
def find_music_files(music_folder):

    music_folder = Path(music_folder)

    if not music_folder.is_dir():
        return ListaEncadeada()

    music_files = ListaEncadeada()

    for root, dirs, files in os.walk(music_folder):

        for filename in files:

            extension = Path(filename).suffix.lower()

            if extension in AUDIO_EXTENSIONS:
                music_files.inserir_fim(
                    os.path.join(root, filename)
                )

    return music_files
