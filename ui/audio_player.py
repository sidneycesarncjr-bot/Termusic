
import json
import os
import socket
import subprocess
import tempfile
import time


class AudioPlayer:

    def __init__(self):
        self.process = None

        self.socket_path = os.path.join(
            tempfile.gettempdir(),
            f"termusic-{os.getpid()}.sock"
        )

    def start(self):

        if self.process and self.process.poll() is None:
            return

        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        self.process = subprocess.Popen(
            [
                "mpv",
                "--idle=yes",
                "--no-video",
                "--no-terminal",
                "--force-window=no",
                f"--input-ipc-server={self.socket_path}"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        for _ in range(50):

            if os.path.exists(self.socket_path):
                return

            if self.process.poll() is not None:
                raise RuntimeError("Não foi possível iniciar o MPV.")

            time.sleep(0.1)

        raise RuntimeError("Tempo esgotado ao iniciar o MPV.")

    def command(self, command):

        self.start()

        message = json.dumps({
            "command": command
        }) + "\n"

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:

            connection.settimeout(3)
            connection.connect(self.socket_path)
            connection.sendall(message.encode("utf-8"))

            response = connection.recv(4096).decode("utf-8")

            result = json.loads(response)

            if result.get("error") != "success":
                raise RuntimeError(f"Erro no MPV: {result}")

    def play(self, music_path):

        self.command([
            "loadfile",
            os.path.abspath(music_path),
            "replace"
        ])

    def pause(self):

        self.command(["set_property", "pause", True])

    def resume(self):

        self.command(["set_property", "pause", False])

    def stop(self):

        self.command(["stop"])

    def close(self):

        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=3)

        self.process = None

        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
