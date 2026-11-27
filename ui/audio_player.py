"""Controle multiplataforma do MPV por IPC local."""

import json
import os
import socket
import subprocess
import tempfile
import threading
import time


class AudioPlayer:
    """Controla o MPV por socket Unix ou named pipe do Windows."""

    def __init__(self):
        self.process = None
        self._request_id = 0
        self._command_lock = threading.Lock()
        if os.name == "nt":
            # No Windows, o MPV cria o IPC no namespace de named pipes.
            self.ipc_path = rf"\\.\pipe\termusic-{os.getpid()}"
        else:
            self.ipc_path = os.path.join(
                tempfile.gettempdir(),
                f"termusic-{os.getpid()}.sock",
            )

    def _ipc_disponivel(self):
        if os.name == "nt":
            import ctypes

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.WaitNamedPipeW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32]
            kernel32.WaitNamedPipeW.restype = ctypes.c_int
            return bool(kernel32.WaitNamedPipeW(self.ipc_path, 100))
        return os.path.exists(self.ipc_path)

    def start(self):
        if self.process and self.process.poll() is None:
            return

        if os.name != "nt" and os.path.exists(self.ipc_path):
            os.remove(self.ipc_path)

        self.process = subprocess.Popen(
            [
                "mpv",
                "--idle=yes",
                "--no-video",
                "--no-terminal",
                "--force-window=no",
                "--keep-open=yes",
                f"--input-ipc-server={self.ipc_path}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        limite = time.monotonic() + 5
        while time.monotonic() < limite:
            if self._ipc_disponivel():
                return
            if self.process.poll() is not None:
                raise RuntimeError(
                    "Não foi possível iniciar o MPV. Confira se ele está instalado e no PATH."
                )
            time.sleep(0.1)

        raise RuntimeError("Tempo esgotado ao iniciar o IPC do MPV.")

    @staticmethod
    def _validar_resposta(linha, request_id):
        resposta = json.loads(linha.decode("utf-8"))
        if resposta.get("request_id") != request_id:
            return False, None
        if resposta.get("error") != "success":
            raise RuntimeError(f"Erro no MPV: {resposta}")
        return True, resposta.get("data")

    def _command_unix(self, mensagem, request_id):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conexao:
            conexao.settimeout(3)
            conexao.connect(self.ipc_path)
            conexao.sendall(mensagem)
            with conexao.makefile("rb") as arquivo:
                while True:
                    linha = arquivo.readline()
                    if not linha:
                        raise RuntimeError("O MPV encerrou a conexão IPC.")
                    encontrada, resultado = self._validar_resposta(
                        linha, request_id
                    )
                    if encontrada:
                        return resultado

    @staticmethod
    def _abrir_named_pipe(caminho):
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.WaitNamedPipeW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD]
        kernel32.WaitNamedPipeW.restype = wintypes.BOOL
        kernel32.CreateFileW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        ]
        kernel32.CreateFileW.restype = wintypes.HANDLE
        kernel32.WriteFile.argtypes = [
            wintypes.HANDLE,
            wintypes.LPCVOID,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            wintypes.LPVOID,
        ]
        kernel32.WriteFile.restype = wintypes.BOOL
        kernel32.ReadFile.argtypes = [
            wintypes.HANDLE,
            wintypes.LPVOID,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            wintypes.LPVOID,
        ]
        kernel32.ReadFile.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL

        # Espera até 3 segundos por uma instância disponível do pipe.
        if not kernel32.WaitNamedPipeW(caminho, 3000):
            erro = ctypes.get_last_error()
            raise OSError(erro, "Não foi possível conectar ao pipe IPC do MPV.")

        generic_read = 0x80000000
        generic_write = 0x40000000
        open_existing = 3
        handle = kernel32.CreateFileW(
            caminho,
            generic_read | generic_write,
            0,
            None,
            open_existing,
            0,
            None,
        )
        if handle == wintypes.HANDLE(-1).value:
            erro = ctypes.get_last_error()
            raise OSError(erro, "Não foi possível abrir o pipe IPC do MPV.")
        return kernel32, handle

    def _command_windows(self, mensagem, request_id):
        import ctypes
        from ctypes import wintypes

        kernel32, handle = self._abrir_named_pipe(self.ipc_path)
        try:
            escritos = wintypes.DWORD()
            buffer_saida = ctypes.create_string_buffer(mensagem)
            if not kernel32.WriteFile(
                handle,
                buffer_saida,
                len(mensagem),
                ctypes.byref(escritos),
                None,
            ):
                erro = ctypes.get_last_error()
                raise OSError(erro, "Falha ao enviar comando ao MPV.")

            restante = bytearray()
            buffer = ctypes.create_string_buffer(4096)
            while True:
                lidos = wintypes.DWORD()
                if not kernel32.ReadFile(
                    handle,
                    buffer,
                    len(buffer),
                    ctypes.byref(lidos),
                    None,
                ):
                    erro = ctypes.get_last_error()
                    raise OSError(erro, "Falha ao receber resposta do MPV.")
                if lidos.value == 0:
                    raise RuntimeError("O MPV encerrou a conexão IPC.")

                restante.extend(buffer.raw[: lidos.value])
                while b"\n" in restante:
                    linha, _, restante = restante.partition(b"\n")
                    if not linha:
                        continue
                    encontrada, resultado = self._validar_resposta(
                        linha, request_id
                    )
                    if encontrada:
                        return resultado
        finally:
            kernel32.CloseHandle(handle)

    def command(self, command):
        with self._command_lock:
            self.start()
            self._request_id += 1
            request_id = self._request_id
            mensagem = (
                json.dumps({
                    "command": command,
                    "request_id": request_id,
                })
                + "\n"
            ).encode("utf-8")

            if os.name == "nt":
                return self._command_windows(mensagem, request_id)
            return self._command_unix(mensagem, request_id)

    def play(self, music_path):
        self.command([
            "loadfile",
            os.path.abspath(music_path),
            "replace",
        ])
        # O MPV pode aceitar loadfile antes de atualizar eof-reached. Aguarda
        # o novo arquivo sair do estado EOF para não confundir a faixa anterior.
        limite = time.monotonic() + 5
        while time.monotonic() < limite:
            try:
                if not self.is_ended():
                    return
            except RuntimeError as error:
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

            if os.name != "nt" and os.path.exists(self.ipc_path):
                os.remove(self.ipc_path)
