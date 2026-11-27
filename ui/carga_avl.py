"""Carga 5.000 faixas na AVL e informa a altura resultante."""

from ui.arvore_avl import ArvoreAVL
from ui.faixa import Faixa


def executar_carga(quantidade=5000):
    arvore = ArvoreAVL("titulo")
    for indice in range(quantidade):
        faixa = Faixa(
            f"Faixa {indice:05d}",
            "Artista de carga",
            indice % 600,
            f"carga://{indice}",
        )
        arvore.inserir(faixa)

    print(f"Faixas inseridas: {len(arvore)}")
    print(f"Altura da AVL: {arvore.altura()}")
    return arvore.altura()


if __name__ == "__main__":
    executar_carga()
