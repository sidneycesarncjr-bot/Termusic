class NoPilha:
    def __init__(self, faixa):
        self.faixa = faixa
        self.proximo = None


class HistoricoPilha:
    """Pilha manual LIFO para as faixas tocadas mais recentemente."""

    def __init__(self, limite=None):
        if limite is not None and limite < 0:
            raise ValueError("O limite do histórico não pode ser negativo.")
        self.topo = None
        self.tamanho = 0
        self.limite = limite

    def push(self, faixa):
        novo = NoPilha(faixa)
        novo.proximo = self.topo
        self.topo = novo
        self.tamanho += 1

        if self.limite is not None and self.tamanho > self.limite:
            self._remover_fundo()

    def _remover_fundo(self):
        if self.topo is None:
            return
        if self.topo.proximo is None:
            self.topo = None
            self.tamanho = 0
            return

        atual = self.topo
        while atual.proximo.proximo is not None:
            atual = atual.proximo
        atual.proximo = None
        self.tamanho -= 1

    def pop(self):
        if self.topo is None:
            return None
        faixa = self.topo.faixa
        self.topo = self.topo.proximo
        self.tamanho -= 1
        return faixa

    def peek(self):
        return None if self.topo is None else self.topo.faixa

    def listar(self):
        atual = self.topo
        while atual is not None:
            yield atual.faixa
            atual = atual.proximo

    def vazia(self):
        return self.topo is None

    def __len__(self):
        return self.tamanho
