"""Fila FIFO de faixas que aguardam reprodução."""


class NoFila:
    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class Fila:
    def __init__(self):
        self.inicio = None
        self.fim = None
        self._tamanho = 0

    def esta_vazia(self):
        return self.inicio is None

    def __len__(self):
        return self._tamanho

    def enfileirar(self, dado):
        """Insere no fim da fila em O(1)."""
        novo = NoFila(dado)
        if self.fim is None:
            self.inicio = novo
        else:
            self.fim.proximo = novo
        self.fim = novo
        self._tamanho += 1

    def desenfileirar(self):
        """Remove e retorna o primeiro item, ou None se estiver vazia."""
        if self.inicio is None:
            return None

        no = self.inicio
        self.inicio = no.proximo
        if self.inicio is None:
            self.fim = None
        no.proximo = None
        self._tamanho -= 1
        return no.dado

    def frente(self):
        """Retorna o primeiro item sem removê-lo."""
        return None if self.inicio is None else self.inicio.dado

    def __iter__(self):
        no = self.inicio
        while no is not None:
            yield no.dado
            no = no.proximo

    def limpar(self):
        """Remove todos os itens da fila."""
        self.inicio = None
        self.fim = None
        self._tamanho = 0
