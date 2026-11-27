import json
import os
import socket
import subprocess
import tempfile
import threading
import time


class AudioPlayer:
    """Controla o MPV por IPC local."""

    def __init__(self):
        self.process = None
        self._request_id = 0
        self._command_lock = threading.Lock()
        self.socket_path = os.path.join(
            tempfile.gettempdir(),
            f"termusic-{os.getpid()}.sock",
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
                "--keep-open=yes",
                f"--input-ipc-server={self.socket_path}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        for _ in range(50):
            if os.path.exists(self.socket_path):
                return
            if self.process.poll() is not None:
                raise RuntimeError("Não foi possível iniciar o MPV.")
            time.sleep(0.1)

        raise RuntimeError("Tempo esgotado ao iniciar o MPV.")

    def command(self, command):
        with self._command_lock:
            self.start()
            self._request_id += 1
            request_id = self._request_id
            mensagem = json.dumps({
                "command": command,
                "request_id": request_id,
            }) + "\n"

            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conexao:
                conexao.settimeout(3)
                conexao.connect(self.socket_path)
                conexao.sendall(mensagem.encode("utf-8"))
                with conexao.makefile("rb") as arquivo:
                    while True:
                        linha = arquivo.readline()
                        if not linha:
                            raise RuntimeError("O MPV encerrou a conexão IPC.")
                        resposta = json.loads(linha.decode("utf-8"))
                        if resposta.get("request_id") != request_id:
                            continue
                        if resposta.get("error") != "success":
                            raise RuntimeError(f"Erro no MPV: {resposta}")
                        return resposta.get("data")

    def play(self, music_path):
        self.command([
            "loadfile",
            os.path.abspath(music_path),
            "replace",
        ])
        # O MPV pode aceitar loadfile antes de atualizar eof-reached. Aguarda
        # o novo arquivo sair do estado EOF para o monitor não avançar/repetir
        # com base no término da faixa anterior.
        limite = time.monotonic() + 5
        while time.monotonic() < limite:
            try:
                if not self.is_ended():
                    return
            except RuntimeError as error:
                # eof-reached pode ficar indisponível enquanto o MPV abre o
                # arquivo. Nesse intervalo, continue aguardando o carregamento.
                if "property unavailable" not in str(error).lower():
                    raise
            time.sleep(0.05)
        raise RuntimeError("O MPV não iniciou a nova faixa (EOF não foi limpo).")

    def pause(self):
        self.command(["set_property", "pause", True])

    def resume(self):
        self.command(["set_property", "pause", False])

    def is_paused(self):
        return bool(self.command(["get_property", "pause"]))

    def is_ended(self):
        return bool(self.command(["get_property", "eof-reached"]))

    def stop(self):
        if self.process and self.process.poll() is None:
            self.command(["stop"])

    def close(self):
        with self._command_lock:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=3)
            self.process = None

            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)
