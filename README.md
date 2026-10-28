# Marisqueiras da Ilha

Projeto da disciplina de **Programação Orientada a Objetos** (docente: Aline Maya).
Sistema **B2B** que apoia a venda direta de mariscos entre **empresas marisqueiras** (fornecedoras) e **empresas compradoras**. Não atende consumidor final.

> **Escopo:** modelagem orientada a objetos e regras de negócio (RN01 a RN23), tudo em memória. Não há banco de dados, tela, pagamento nem rastreamento de entrega em tempo real.

---

## Como rodar

Só é necessário o Python 3 (nenhuma biblioteca externa). Na pasta do projeto:

```bash
python main.py        # demonstração do fluxo completo
python testes.py      # testes pelo terminal (as regras de negócio)
python simulador.py   # simulador interativo: você digita os dados
```

O `testes.py` termina com `TUDO CERTO` quando todas as verificações passam. Os blocos **FIGURA 1**, **FIGURA 2** e **FIGURA 3** da saída são os usados nos prints do artigo.

## Estrutura

```text
.
├── empresa.py        # Empresa, EmpresaMarisqueira, EmpresaCompradora
├── produto.py        # Produto
├── pedido.py         # Pedido, ItemPedido
├── avaliacao.py      # Avaliacao
├── main.py           # demonstração do fluxo
├── testes.py         # testes das regras de negócio
├── simulador.py      # simulador interativo por perfil
├── MODELAGEM_POO.md  # classes, UML, decisões e rastreabilidade RN -> método -> teste
└── README.md         # este arquivo
```

## Classes

| Classe | Papel |
|---|---|
| `Empresa` | Superclasse: CNPJ, nome e localização. |
| `EmpresaMarisqueira` | Fornece, analisa pedidos (aceita, rejeita, pede ajuste) e atualiza a entrega. |
| `EmpresaCompradora` | Consulta e compara produtos, envia pedidos e avalia a marisqueira. |
| `Produto` | Marisco vendido por kg. Fresco e congelado são produtos diferentes. |
| `ItemPedido` | Liga um pedido a um produto, com a quantidade e o preço do momento. |
| `Pedido` | Pedido de uma compradora a **uma** marisqueira. |
| `Avaliacao` | Nota de 1 a 5 estrelas dada à marisqueira. |

Atributos, métodos, associações e diagrama UML estão em [`MODELAGEM_POO.md`](MODELAGEM_POO.md).

## Regras de negócio garantidas

| RN | Regra | Como o código garante |
|---|---|---|
| RN05, RN15 | Mínimo de 25 kg **por produto** | `ItemPedido.validar_quantidade` |
| RN06 | Fresco e congelado são produtos diferentes | Categoria validada; nome + categoria não se repetem |
| RN07 | Preço não muda durante a venda | O item guarda uma cópia do preço |
| RN08 | Estoque alterável a qualquer momento | `alterar_quantidade` (nunca negativo) |
| RN09, RN19 | Estoque zero: continua cadastrado como indisponível | `get_status()` |
| RN10, RN11 | Busca com filtros e ordenação | `consultar_produtos` |
| RN12 | Marisqueira vê só os próprios produtos; compradora compara | `produtos` por empresa; `comparar_produtos` |
| RN13 | Pedido com compradora, itens, endereço e tempo de entrega | `Pedido.__init__` |
| RN14 | Um pedido não mistura marisqueiras | `Pedido.adicionar_item` |
| RN16 | Não há valor mínimo | Só existe regra por quantidade |
| RN17, RN18 | Limite é o estoque; o sistema bloqueia e informa | `adicionar_item` e `aceitar_pedido` |
| RN20 | Indicador verde / laranja / vermelho | `situacao()` |
| RN21 | Avaliação de 1 a 5, após a compra | `avaliar_empresa` + `registrar_nota` |
| RN22 | Entrega pela marisqueira, com status | `atualizar_status_entrega` |
| RN23 | Custo da entrega no preço | Garantida por omissão: não há campo de frete |

RN01 a RN03 são restrições organizacionais garantidas pela estrutura (só existem marisqueira e compradora). A tabela completa, com o teste de cada regra, está no `MODELAGEM_POO.md`.

## Fluxo do pedido

```text
pendente ──aceitar──────▶ em preparo ──▶ em curso ──▶ finalizado
   │  ▲
   │  └── reenviar (compradora) ──┐
   ├──pedir ajuste──▶ ajuste solicitado
   └──rejeitar──────▶ rejeitado
```

- O **estoque só é debitado no aceite**, depois de conferir de novo a disponibilidade.
- O status só muda por `alterar_status()`, que recusa qualquer transição fora do fluxo.
- A avaliação só é permitida com o pedido **finalizado**, uma vez por pedido.

## Pilares de POO

- **Encapsulamento:** estoque do `Produto` e status do `Pedido` são privados e só mudam por métodos que aplicam as regras.
- **Herança:** `EmpresaMarisqueira` e `EmpresaCompradora` herdam de `Empresa`.
- **Polimorfismo:** `descrever()` é sobrescrito em cada subclasse.
- **Associação e composição:** `Pedido` contém `ItemPedido`; `ItemPedido` refere-se a um `Produto`.
- **Exceções:** regra violada gera `ValueError` com mensagem clara, tratada com `try/except`.

## Decisões de modelagem

As principais (lista completa no `MODELAGEM_POO.md`):

1. O estoque (`quantidade_disponivel`) fica em `Produto`.
2. O cadastro exige 25 kg (P19); depois das vendas o estoque pode cair abaixo disso ou chegar a zero.
3. Foram acrescentados os status **pendente**, **ajuste solicitado** e **rejeitado** aos três do documento (em preparo, em curso, finalizado) para representar a análise do pedido (P7).
4. Estoque baixo (RN20) significa nenhum produto com 25 kg ou mais.
5. Uma avaliação por pedido (o documento não define a cardinalidade).
6. Proximidade (RN11) é a mesma localização da compradora; não há coordenadas.
