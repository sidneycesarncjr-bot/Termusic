"""Modelo de faixa compartilhado pela tabela hash e pela árvore AVL."""


class Faixa:
    _proximo_id = 1

    def __init__(self, titulo, artista, duracao, caminho=None, capa=None):
        self.titulo = titulo
        self.artista = artista
        self.duracao = duracao  # segundos; None quando a duração é desconhecida
        self.caminho = caminho
        self.capa = capa
        self.id = Faixa._proximo_id
        Faixa._proximo_id += 1

    @property
    def title(self):
        return self.titulo

    @property
    def artist(self):
        return self.artista

    @property
    def duration(self):
        if self.duracao is None:
            return "--:--"
        minutos, segundos = divmod(self.duracao, 60)
        return f"{minutos:02d}:{segundos:02d}"

    @property
    def path(self):
        return self.caminho

    @property
    def cover(self):
        return self.capa

    def get(self, chave, padrao=None):
        if chave == "title":
            atributo = "titulo"
        elif chave == "artist":
            atributo = "artista"
        elif chave == "duration":
            return self.duration
        elif chave == "path":
            atributo = "caminho"
        elif chave == "cover":
            atributo = "capa"
        else:
            atributo = chave
        return getattr(self, atributo, padrao)

    def __getitem__(self, chave):
        valor = self.get(chave)
        if valor is None and chave not in ("cover", "capa"):
            raise KeyError(chave)
        return valor

    def __str__(self):
        if self.duracao is None:
            tempo = "--:--"
        else:
            minutos, segundos = divmod(self.duracao, 60)
            tempo = f"{minutos}:{segundos:02d}"
        return f"{self.titulo} — {self.artista} ({tempo})"

    __repr__ = __str__
