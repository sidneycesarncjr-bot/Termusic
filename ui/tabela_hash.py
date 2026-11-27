"""Tabela hash manual com encadeamento separado e busca por título."""

from ui.text_utils import normalizar


class NoHash:
    def __init__(self, chave, faixa):
        self.chave = chave
        self.faixa = faixa
        self.prox = None


class TabelaHash:
    CAPACIDADE_INICIAL = 11
    FATOR_CARGA_MAX = 0.75

    def __init__(self, capacidade=CAPACIDADE_INICIAL):
        if not isinstance(capacidade, int) or capacidade < 1:
            raise ValueError("A capacidade deve ser um inteiro positivo.")
        self.capacidade = capacidade
        # Vetor fixo de baldes; as colisões são guardadas em nós encadeados.
        self.baldes = [None] * capacidade
        self.tamanho = 0

    @staticmethod
    def _normalizar(titulo):
        return normalizar(titulo)

    @staticmethod
    def _titulo(faixa):
        return getattr(faixa, "titulo", getattr(faixa, "title", ""))

    @staticmethod
    def _identificador(faixa):
        return getattr(faixa, "id", getattr(faixa, "path", None))

    def _mesma_faixa(self, a, b):
        id_a = self._identificador(a)
        id_b = self._identificador(b)
        if id_a is not None and id_b is not None:
            return id_a == id_b
        return a is b

    def _hash(self, chave):
        # Hash polinomial de base 31; calcula em O(tamanho do título).
        valor = 0
        for caractere in chave:
            valor = (valor * 31 + ord(caractere)) % self.capacidade
        return valor

    def inserir(self, faixa):
        chave = self._normalizar(self._titulo(faixa))
        indice = self._hash(chave)

        atual = self.baldes[indice]
        while atual is not None:
            if atual.chave == chave and self._mesma_faixa(atual.faixa, faixa):
                atual.faixa = faixa
                return False
            atual = atual.prox

        if (self.tamanho + 1) / self.capacidade > self.FATOR_CARGA_MAX:
            self._redimensionar()
            indice = self._hash(chave)

        novo = NoHash(chave, faixa)
        novo.prox = self.baldes[indice]
        self.baldes[indice] = novo
        self.tamanho += 1
        return True

    def buscar(self, titulo):
        """Itera por todas as faixas com esse título, sem criar lista auxiliar."""
        chave = self._normalizar(titulo)
        atual = self.baldes[self._hash(chave)]
        while atual is not None:
            if atual.chave == chave:
                yield atual.faixa
            atual = atual.prox

    def buscar_primeira(self, titulo):
        return next(self.buscar(titulo), None)

    def contem(self, titulo):
        return self.buscar_primeira(titulo) is not None

    def remover(self, faixa):
        chave = self._normalizar(self._titulo(faixa))
        indice = self._hash(chave)
        anterior = None
        atual = self.baldes[indice]

        while atual is not None:
            if atual.chave == chave and self._mesma_faixa(atual.faixa, faixa):
                if anterior is None:
                    self.baldes[indice] = atual.prox
                else:
                    anterior.prox = atual.prox
                atual.prox = None
                self.tamanho -= 1
                return True
            anterior, atual = atual, atual.prox
        return False

    @staticmethod
    def _proximo_primo(numero):
        def eh_primo(valor):
            if valor < 2:
                return False
            divisor = 2
            while divisor * divisor <= valor:
                if valor % divisor == 0:
                    return False
                divisor += 1
            return True

        while not eh_primo(numero):
            numero += 1
        return numero

    def _redimensionar(self):
        baldes_antigos = self.baldes
        self.capacidade = self._proximo_primo(self.capacidade * 2)
        self.baldes = [None] * self.capacidade

        for primeiro in baldes_antigos:
            atual = primeiro
            while atual is not None:
                proximo = atual.prox
                indice = self._hash(atual.chave)
                atual.prox = self.baldes[indice]
                self.baldes[indice] = atual
                atual = proximo

    def fator_carga(self):
        return self.tamanho / self.capacidade

    def __len__(self):
        return self.tamanho

    def __iter__(self):
        for primeiro in self.baldes:
            atual = primeiro
            while atual is not None:
                yield atual.faixa
                atual = atual.prox
