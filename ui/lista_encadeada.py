"""Lista simplesmente encadeada manual para coleções de faixas."""


class NoLista:
    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class ListaEncadeada:
    def __init__(self):
        self.inicio = None
        self.fim = None
        self.tamanho = 0

    def esta_vazia(self):
        return self.inicio is None

    def __len__(self):
        return self.tamanho

    def inserir_fim(self, dado):
        novo = NoLista(dado)
        if self.fim is None:
            self.inicio = novo
        else:
            self.fim.proximo = novo
        self.fim = novo
        self.tamanho += 1

    def __iter__(self):
        atual = self.inicio
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    def __getitem__(self, indice):
        if indice < 0:
            indice += self.tamanho
        if not 0 <= indice < self.tamanho:
            raise IndexError("índice fora da lista")

        atual = self.inicio
        for _ in range(indice):
            atual = atual.proximo
        return atual.dado
