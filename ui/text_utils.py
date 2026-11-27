import unicodedata


def normalizar(texto):
    """Remove acentos e padroniza caixa e espaços para comparações."""
    sem_acento = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(
        caractere
        for caractere in sem_acento
        if unicodedata.category(caractere) != "Mn"
    )
    return " ".join(sem_acento.casefold().split())
