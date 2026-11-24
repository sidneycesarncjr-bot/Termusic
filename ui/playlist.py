"""Lista circular usada para navegar pelas faixas da playlist."""


class No:
    """Nó de uma lista duplamente encadeada."""

    def __init__(self, dado):
        self.dado = dado
        self.anterior = None
        self.proximo = None


class ListaDuplamenteCircular:
    def __init__(self):
        self.fim = None
        self.tamanho = 0
        self.atual = None

    def esta_vazia(self):
        return self.tamanho == 0

    def __len__(self):
        return self.tamanho

    @staticmethod
    def _mesma_faixa(a, b):
        """Compara faixas pelo caminho; usa igualdade para outros tipos."""
        if isinstance(a, dict) and isinstance(b, dict):
            caminho_a = a.get("path")
            caminho_b = b.get("path")
            if caminho_a is not None and caminho_b is not None:
                return caminho_a == caminho_b
        return a == b

    def inserir_fim(self, dado):
        novo = No(dado)
        if self.fim is None:
            novo.anterior = novo
            novo.proximo = novo
            self.fim = novo
        else:
            primeiro = self.fim.proximo
            novo.proximo = primeiro
            novo.anterior = self.fim
            self.fim.proximo = novo
            primeiro.anterior = novo
            self.fim = novo
        self.tamanho += 1
        if self.atual is None:
            self.atual = novo
        return novo

    def inserir_inicio(self, dado):
        novo = No(dado)
        if self.fim is None:
            novo.anterior = novo
            novo.proximo = novo
            self.fim = novo
        else:
            primeiro = self.fim.proximo
            novo.proximo = primeiro
            novo.anterior = self.fim
            primeiro.anterior = novo
            self.fim.proximo = novo
        self.tamanho += 1
        if self.atual is None:
            self.atual = novo
        return novo

    def buscar(self, dado):
        if self.fim is None:
            return None
        no = self.fim.proximo
        for _ in range(self.tamanho):
            if self._mesma_faixa(no.dado, dado):
                return no
            no = no.proximo
        return None

    def _remover_no(self, no):
        proxima_atual = no.proximo if self.tamanho > 1 else None
        if self.tamanho == 1:
            self.fim = None
            self.atual = None
        else:
            no.anterior.proximo = no.proximo
            no.proximo.anterior = no.anterior
            if no is self.fim:
                self.fim = no.anterior
            if no is self.atual:
                self.atual = proxima_atual

        no.anterior = None
        no.proximo = None
        self.tamanho -= 1

    def remover(self, dado):
        no = self.buscar(dado)
        if no is None:
            return False
        self._remover_no(no)
        return True

    def remover_indice(self, indice):
        no = self.no_no_indice(indice)
        if no is None:
            return None
        dado = no.dado
        self._remover_no(no)
        return dado

    def no_no_indice(self, indice):
        if not 0 <= indice < self.tamanho:
            return None
        no = self.fim.proximo
        for _ in range(indice):
            no = no.proximo
        return no

    def item_no_indice(self, indice):
        no = self.no_no_indice(indice)
        return None if no is None else no.dado

    def tocar_atual(self):
        return None if self.atual is None else self.atual.dado

    def proxima(self):
        if self.atual is None:
            return None
        self.atual = self.atual.proximo
        return self.atual.dado

    def anterior(self):
        if self.atual is None:
            return None
        self.atual = self.atual.anterior
        return self.atual.dado

    def definir_atual(self, dado):
        no = self.buscar(dado)
        if no is None:
            return False
        self.atual = no
        return True

    def definir_atual_indice(self, indice):
        no = self.no_no_indice(indice)
        if no is None:
            return False
        self.atual = no
        return True

    def indice_atual(self):
        if self.atual is None:
            return None
        no = self.fim.proximo
        for indice in range(self.tamanho):
            if no is self.atual:
                return indice
            no = no.proximo
        return None

    def __iter__(self):
        if self.fim is None:
            return
        no = self.fim.proximo
        for _ in range(self.tamanho):
            yield no.dado
            no = no.proximo

    @staticmethod
    def _descricao(dado):
        if isinstance(dado, dict):
            titulo = dado.get("title", "Faixa desconhecida")
            artista = dado.get("artist", "Artista desconhecido")
            return f"{titulo} — {artista}"
        return str(dado)

    def exibir(self):
        if self.esta_vazia():
            print("[playlist vazia]")
            return
        no = self.fim.proximo
        for indice in range(1, self.tamanho + 1):
            marcador = "▶ " if no is self.atual else "  "
            print(f"{marcador}{indice}. {self._descricao(no.dado)}")
            no = no.proximo
