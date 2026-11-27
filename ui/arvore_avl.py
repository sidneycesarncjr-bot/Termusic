"""Árvore AVL manual para ordenar e buscar faixas por título ou duração."""

from ui.text_utils import normalizar


class NoAVL:
    def __init__(self, faixa, chave):
        self.faixa = faixa
        self.chave = chave
        self.esq = None
        self.dir = None
        self.altura = 1


class ArvoreAVL:
    CRITERIOS = ("titulo", "duracao")

    def __init__(self, criterio="titulo"):
        if criterio not in self.CRITERIOS:
            raise ValueError("criterio deve ser 'titulo' ou 'duracao'")
        self.criterio = criterio
        self.raiz = None
        self.tamanho = 0

    def _valor(self, faixa_ou_valor):
        if hasattr(faixa_ou_valor, "titulo"):
            if self.criterio == "titulo":
                return normalizar(faixa_ou_valor.titulo)
            return (
                faixa_ou_valor.duracao
                if faixa_ou_valor.duracao is not None
                else -1
            )
        if self.criterio == "titulo":
            return normalizar(str(faixa_ou_valor))
        return faixa_ou_valor

    def _chave(self, faixa):
        return (self._valor(faixa), faixa.id)

    @staticmethod
    def _altura(no):
        return no.altura if no is not None else 0

    def _atualizar_altura(self, no):
        no.altura = 1 + max(self._altura(no.esq), self._altura(no.dir))

    def _fator_balanceamento(self, no):
        if no is None:
            return 0
        return self._altura(no.esq) - self._altura(no.dir)

    def _rotacao_direita(self, y):
        x = y.esq
        subarvore = x.dir
        x.dir = y
        y.esq = subarvore
        self._atualizar_altura(y)
        self._atualizar_altura(x)
        return x

    def _rotacao_esquerda(self, x):
        y = x.dir
        subarvore = y.esq
        y.esq = x
        x.dir = subarvore
        self._atualizar_altura(x)
        self._atualizar_altura(y)
        return y

    def _balancear(self, no):
        self._atualizar_altura(no)
        fator = self._fator_balanceamento(no)

        if fator > 1:
            if self._fator_balanceamento(no.esq) < 0:
                no.esq = self._rotacao_esquerda(no.esq)
            return self._rotacao_direita(no)

        if fator < -1:
            if self._fator_balanceamento(no.dir) > 0:
                no.dir = self._rotacao_direita(no.dir)
            return self._rotacao_esquerda(no)

        return no

    def inserir(self, faixa):
        if self.buscar(faixa) is not None:
            return False
        self.raiz = self._inserir(self.raiz, faixa, self._chave(faixa))
        self.tamanho += 1
        return True

    def _inserir(self, no, faixa, chave):
        if no is None:
            return NoAVL(faixa, chave)
        if chave < no.chave:
            no.esq = self._inserir(no.esq, faixa, chave)
        elif chave > no.chave:
            no.dir = self._inserir(no.dir, faixa, chave)
        else:
            # IDs únicos evitam chaves iguais; não duplica a mesma faixa.
            return no
        return self._balancear(no)

    def buscar(self, valor):
        """Busca por valor do critério; aceita Faixa para busca exata por ID."""
        atual = self.raiz
        if hasattr(valor, "titulo"):
            chave = self._chave(valor)
            while atual is not None:
                if chave == atual.chave:
                    return atual.faixa
                atual = atual.esq if chave < atual.chave else atual.dir
            return None

        alvo = self._valor(valor)
        while atual is not None:
            valor_no = atual.chave[0]
            if alvo == valor_no:
                return atual.faixa
            atual = atual.esq if alvo < valor_no else atual.dir
        return None

    def contem(self, valor):
        return self.buscar(valor) is not None

    def remover(self, faixa):
        antes = self.tamanho
        self.raiz = self._remover(self.raiz, self._chave(faixa))
        return self.tamanho < antes

    def _remover(self, no, chave):
        if no is None:
            return None

        if chave < no.chave:
            no.esq = self._remover(no.esq, chave)
        elif chave > no.chave:
            no.dir = self._remover(no.dir, chave)
        else:
            self.tamanho -= 1
            if no.esq is None:
                return no.dir
            if no.dir is None:
                return no.esq

            sucessor = no.dir
            while sucessor.esq is not None:
                sucessor = sucessor.esq
            no.faixa = sucessor.faixa
            no.chave = sucessor.chave
            # O sucessor será removido recursivamente; compensa o contador.
            self.tamanho += 1
            no.dir = self._remover(no.dir, sucessor.chave)

        return self._balancear(no)

    def listar(self, decrescente=False):
        """Itera em ordem, sem criar uma lista auxiliar."""
        def percorrer(no):
            if no is None:
                return
            primeiro = no.dir if decrescente else no.esq
            segundo = no.esq if decrescente else no.dir
            yield from percorrer(primeiro)
            yield no.faixa
            yield from percorrer(segundo)

        yield from percorrer(self.raiz)

    def altura(self):
        return self._altura(self.raiz)

    def __len__(self):
        return self.tamanho
