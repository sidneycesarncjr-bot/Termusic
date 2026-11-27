# Termusic

Player de música em modo texto para o Projeto Prático Final da disciplina de Estrutura de Dados da UFAL, Campus Arapiraca.

## Integrantes e divisão de tarefas

Integrantes do grupo e responsabilidades no projeto:

| Integrante | Tarefas |
|---|---|
| Sidney César | Front-end e interface do aplicativo |
| Luiz Gabriel | Lista duplamente encadeada circular e fila |
| César Ferreira | Pilha do histórico |
| Nycollas Rannyeri | Tabela hash e árvore AVL |

## Tema

Player de música com biblioteca local, playlist circular, fila “tocar a seguir” e histórico.

## Requisitos

- Python 3.10 ou superior.
- MPV instalado e disponível no `PATH`; o programa o controla pelo socket IPC local.
- Dependências Python listadas em `requirements.txt`.

## Como executar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Instale o MPV separadamente antes de iniciar o aplicativo. O controle atual do MPV usa socket Unix, então a execução suportada é em Linux ou macOS.

## Controles

- Na navegação lateral: setas para cima/baixo e `Enter`.
- Na Biblioteca: escolha uma pasta, pesquise pelo título ou artista e use `Enter` para tocar.
- Pressione `Tab` para alternar entre o campo de pesquisa e a lista.
- Na lista: `Q` adiciona à fila, `P` adiciona à playlist, `O` alterna a ordenação da AVL, `N`/`B` avançam/voltam, `Espaço` pausa/retoma e `R` alterna repetição.
- Na Playlist: setas para cima/baixo selecionam; `Enter` toca; setas esquerda/direita avançam/voltam; `Delete` remove a faixa selecionada.
- A repetição alterna entre desligada (`off`), faixa atual (`one`) e playlist circular (`all`).

## Estruturas de dados

| Estrutura e operação | Melhor caso | Pior caso |
|---|---:|---:|
| Lista encadeada: inserir no fim | O(1) | O(1) |
| Lista encadeada: buscar/acessar por índice | O(1) | O(n) |
| Fila: enfileirar/desenfileirar | O(1) | O(1) |
| Pilha: push/pop/consultar topo | O(1) | Push pode ser O(n) quando o limite é atingido e é preciso descartar a faixa mais antiga |
| Lista circular: inserir nas pontas e avançar/voltar | O(1) | O(1) |
| Lista circular: buscar/remover por faixa | O(1) | O(n) |
| Hash: buscar/inserir/remover (k = comprimento do título) | O(k) esperado | O(n + k) com colisões; redimensionar custa O(n) |
| AVL: buscar | O(1), se a raiz for a chave | O(log n) |
| AVL: inserir/remover | O(1) em caso imediato | O(log n), com a árvore balanceada |
| AVL: listar em ordem | O(n) | O(n) |

As árvores AVL armazenam o mesmo catálogo em dois índices, um por título e outro por duração, para alternar a ordenação sem reconstruir a estrutura.

### Escolhas e custos

- A fila mantém início e fim, então inserir e remover pela frente não exigem percorrer os itens.
- A pilha guarda o topo em um nó encadeado; quando atinge o limite de 100 faixas, descartar a mais antiga percorre a pilha.
- A playlist circular mantém uma referência para o último nó e outra para o nó atual. Os links anterior/próximo tornam a navegação O(1).
- A tabela hash normaliza o título removendo acentos, padronizando caixa e espaços. Usa hash polinomial de base 31 e encadeamento separado para colisões; ao ultrapassar fator de carga 0,75, aumenta a capacidade para o próximo primo.
- As árvores AVL usam a chave `(critério, id)` para manter músicas com títulos ou durações iguais. A listagem em ordem fornece o catálogo ordenado; títulos são normalizados antes da comparação.

## Teste de carga da AVL

Execute:

```bash
python -m ui.carga_avl
```

O script insere 5.000 títulos em ordem crescente e informa a quantidade inserida e a altura observada da AVL. A AVL se mantém balanceada, portanto essa altura cresce proporcionalmente a O(log n), em vez de formar uma cadeia linear como uma BST sem balanceamento.

**Resultado observado nesta revisão:** 5.000 faixas inseridas; altura observada: 13. A inserção foi feita em ordem crescente de título; a altura 13 demonstra que a AVL permaneceu balanceada, em vez de formar uma cadeia de 5.000 nós.

## Organização do código

- `ui/fila.py`: fila encadeada.
- `ui/historico.py`: pilha encadeada e histórico.
- `ui/playlist.py`: lista duplamente encadeada circular.
- `ui/tabela_hash.py`: índice por título.
- `ui/arvore_avl.py`: índices ordenados por título e duração.
- `ui/faixa.py` e `ui/lista_encadeada.py`: modelo de faixa e lista simples.
- `ui/audio_player.py`: integração com o MPV.
- `ui/app.py` e `ui/widgets/`: interface e ligação das estruturas ao player.
