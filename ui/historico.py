
import unicodedata


def normalizar(titulo: str) -> str:
    """Remove acentos, padroniza maiúsculas e espaços."""

    sem_acento = unicodedata.normalize("NFD", titulo)

    sem_acento = "".join(
        c for c in sem_acento
        if unicodedata.category(c) != "Mn"
    )

    return " ".join(sem_acento.casefold().split())


class HistoricoPilha:
    """Histórico de músicas reproduzidas (LIFO)."""

    def __init__(self, limite: int | None = None):
        self._itens = []
        self.limite = limite

    def push(self, faixa):
        # Evita repetir a mesma faixa consecutivamente
        if self._itens and self._itens[-1] is faixa:
            return

        self._itens.append(faixa)

        if self.limite is not None:
            while len(self._itens) > self.limite:
                self._itens.pop(0)

    def pop(self):
        return self._itens.pop() if self._itens else None

    def peek(self):
        return self._itens[-1] if self._itens else None

    def listar(self):
        return self._itens[::-1]

    def vazia(self):
        return not self._itens

    def __len__(self):
        return len(self._itens)
