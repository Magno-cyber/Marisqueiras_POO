# Projeto Marisqueiras da Ilha - POO 🦀

Este repositório contém a implementação em **Programação Orientada a Objetos (POO)** do projeto "Marisqueiras da Ilha", desenvolvido através da metodologia de Aprendizagem Baseada em Projetos (PjBL) da UNDB.

## 🎯 Objetivo
Desenvolver uma solução digital em formato B2B (empresa para empresa) para apoiar a comercialização direta de mariscos entre as marisqueiras (fornecedoras da Vila Maresia) e empresas compradoras.

## 🏗️ Estrutura de Classes e Regras de Negócio Implementadas

A modelagem segue estritamente o diagrama e os documentos de requisitos:

*   **Herança:** `EmpresaMarisqueira` e `EmpresaCompradora` herdam os atributos básicos da superclasse `Empresa`.
*   **Regras de Estoque (`Produto` e `EmpresaMarisqueira`):**
    *   Fresco e congelado são cadastrados separadamente.
    *   Quando a quantidade chega a zero, o produto permanece cadastrado, mas é exibido como indisponível.
*   **Restrições de Compra (`Pedido` e `ItemPedido`):**
    *   **Mínimo de 25 kg** obrigatório por produto.
    *   Não é permitido adicionar produtos de **empresas diferentes** em um mesmo pedido.
    *   O pedido só é finalizado se a quantidade solicitada não ultrapassar o estoque.
*   **Logística e Avaliação:**
    *   Status do pedido mapeados: `em preparo`, `em curso`, `finalizado`.
    *   Ao fim, o comprador avalia a transação usando a classe `Avaliacao` (escala de 1 a 5 estrelas).

## 🚀 Como Executar

O projeto foi escrito em Python. Para testar o fluxo comercial e verificar as travas (regras de negócio) funcionando, basta executar o script principal:

```bash
python sistema_marisqueiras.py
```

A execução no terminal irá simular:
1. O cadastro de marisqueiras e restaurantes.
2. A filtragem de produtos (ex: frescos vs congelados).
3. A tentativa de burlar regras (ex: pedir menos de 25kg ou tentar juntar marisqueiras diferentes no mesmo carrinho).
4. O ciclo completo de um pedido aprovado (Aceite -> Entrega -> Avaliação -> Baixa de Estoque).

---
*Projeto desenvolvido para a disciplina ministrada pela docente Aline Maya.*
