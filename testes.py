"""Testes pelo terminal. Rode:  python testes.py
Cada bloco "FIGURA" serve para tirar o print do paper."""

from empresa import EmpresaMarisqueira, EmpresaCompradora
from produto import Produto
from pedido import Pedido, ItemPedido

falhas = 0


def deve_bloquear(descricao, funcao, *argumentos):
    """Executa funcao(*argumentos). O esperado é a regra bloquear com ValueError."""
    global falhas
    try:
        funcao(*argumentos)
        falhas += 1
        print(f"  [FALHOU] {descricao} -> deveria ter sido bloqueado")
    except ValueError as erro:
        print(f"  [OK] {descricao}\n         bloqueado: {erro}")


def deve_passar(descricao, funcao, *argumentos):
    global falhas
    try:
        funcao(*argumentos)
        print(f"  [OK] {descricao}")
    except ValueError as erro:
        falhas += 1
        print(f"  [FALHOU] {descricao} -> erro inesperado: {erro}")


def conferir(descricao, condicao):
    global falhas
    if condicao:
        print(f"  [OK] {descricao}")
    else:
        falhas += 1
        print(f"  [FALHOU] {descricao}")


def novo_cenario():
    m1 = EmpresaMarisqueira("11.111.111/0001-11", "Vila Maresia Mariscos", "Raposa - MA")
    m2 = EmpresaMarisqueira("33.333.333/0001-33", "Ilha Azul Mariscos", "Paço do Lumiar - MA")
    comp = EmpresaCompradora("22.222.222/0001-22", "Restaurante Sabor do Mar", "São Luís - MA")
    sururu = Produto(1, "Sururu Descascado", "fresco", 30.0, 100.0, m1)
    camarao = Produto(2, "Camarão Seco", "congelado", 45.0, 50.0, m1)
    ostra = Produto(3, "Ostra", "fresco", 60.0, 80.0, m2)
    m1.cadastrar_produto(sururu)
    m1.cadastrar_produto(camarao)
    m2.cadastrar_produto(ostra)
    return m1, m2, comp, sururu, camarao, ostra


def entregar_pedido(m1, comp, produto, id_pedido=1):
    """Cria, envia, aceita e entrega um pedido de 25 kg."""
    p = Pedido(id_pedido, "Av Litorânea, 10", "14:00", comp)
    p.adicionar_item(ItemPedido(id_pedido, produto, 25.0))
    comp.realizar_pedido(p, m1)
    m1.aceitar_pedido(p)
    m1.atualizar_status_entrega(p, "em curso")
    m1.atualizar_status_entrega(p, "finalizado")
    return p


# ---------------------------------------------------------------------------
print("\n=== FIGURA 1 - Peso mínimo (RN05) e estoque disponível (RN18) ===")
m1, m2, comp, sururu, camarao, ostra = novo_cenario()
p = Pedido(1, "Av Litorânea, 10", "14:00", comp)
deve_bloquear("10 kg de sururu (mínimo 25 kg)", p.adicionar_item, ItemPedido(1, sururu, 10.0))
deve_bloquear("24,9 kg de sururu", p.adicionar_item, ItemPedido(1, sururu, 24.9))
deve_passar("25 kg de sururu (exatamente o mínimo)", p.adicionar_item, ItemPedido(1, sururu, 25.0))
deve_bloquear("500 kg de camarão (estoque: 50 kg)", p.adicionar_item, ItemPedido(1, camarao, 500.0))

print("\n=== FIGURA 2 - Marisqueira única (RN14) e estoque zerado (RN09) ===")
m1, m2, comp, sururu, camarao, ostra = novo_cenario()
p = Pedido(1, "Av Litorânea, 10", "14:00", comp)
p.adicionar_item(ItemPedido(1, sururu, 30.0))
deve_bloquear("ostra (Ilha Azul) em pedido da Vila Maresia", p.adicionar_item, ItemPedido(1, ostra, 30.0))
deve_passar("outro produto da MESMA marisqueira", p.adicionar_item, ItemPedido(1, camarao, 25.0))

p2 = Pedido(2, "Av Litorânea, 10", "15:00", comp)
p2.adicionar_item(ItemPedido(2, camarao, 50.0))  # todo o estoque do camarão
comp.realizar_pedido(p2, m1)
m1.aceitar_pedido(p2)
conferir(f"estoque do camarão = {camarao.get_quantidade_disponivel()} kg", camarao.get_quantidade_disponivel() == 0)
conferir(f"status do camarão = {camarao.get_status()}", camarao.get_status() == "indisponível")
conferir("produto zerado continua cadastrado", camarao in m1.produtos)
p3 = Pedido(3, "Av Litorânea, 10", "16:00", comp)
deve_bloquear("pedir produto indisponível", p3.adicionar_item, ItemPedido(3, camarao, 25.0))

print("\n=== FIGURA 3 - Avaliação de 1 a 5 estrelas (RN21) ===")
m1, m2, comp, sururu, camarao, ostra = novo_cenario()
entregue = entregar_pedido(m1, comp, sururu)
for nota in (0, 6, -1, 3.5, "5", True):
    deve_bloquear(f"nota {nota!r}", comp.avaliar_empresa, 9, nota, entregue)
deve_passar("nota 5", comp.avaliar_empresa, 1, 5, entregue)
deve_bloquear("avaliar o mesmo pedido de novo", comp.avaliar_empresa, 2, 4, entregue)
conferir("média da marisqueira = 5.0", m1.media_avaliacoes() == 5.0)
ainda_pendente = Pedido(5, "Av Litorânea, 10", "14:00", comp)
deve_bloquear("avaliar pedido que ainda não foi entregue", comp.avaliar_empresa, 3, 5, ainda_pendente)

# ---------------------------------------------------------------------------
print("\n=== CADASTRO (RN06, RN08, P15, P19) ===")
m1, m2, comp, sururu, camarao, ostra = novo_cenario()
deve_bloquear("categoria 'seco'", Produto, 10, "X", "seco", 10.0, 30.0, m1)
deve_bloquear("preço negativo", Produto, 10, "X", "fresco", -5.0, 30.0, m1)
deve_bloquear("nome vazio", Produto, 10, " ", "fresco", 10.0, 30.0, m1)
deve_bloquear("cadastro com 10 kg", Produto, 10, "X", "fresco", 10.0, 10.0, m1)
deve_bloquear("produto repetido (mesmo nome e categoria)", m1.cadastrar_produto, Produto(11, "Sururu Descascado", "fresco", 9.0, 30.0, m1))
deve_passar("mesmo nome em categoria diferente", m1.cadastrar_produto, Produto(12, "Sururu Descascado", "congelado", 33.0, 40.0, m1))
deve_bloquear("cadastrar produto de outra marisqueira", m1.cadastrar_produto, ostra)
conferir("marisqueira vê só os próprios produtos (RN12)", ostra not in m1.produtos and sururu in m1.produtos)
deve_bloquear("alterar quantidade para negativa", m1.alterar_quantidade, sururu, -5)
deve_bloquear("alterar quantidade de produto de outra empresa", m1.alterar_quantidade, ostra, 40)
m1.alterar_quantidade(sururu, 0)
conferir("quantidade 0 deixa o produto indisponível, mas cadastrado", sururu.get_status() == "indisponível" and sururu in m1.produtos)

print("\n=== PEDIDO E STATUS (RN13, RN16, RN22) ===")
m1, m2, comp, sururu, camarao, ostra = novo_cenario()
deve_bloquear("pedido sem endereço", Pedido, 1, "", "14:00", comp)
p = Pedido(1, "Av Litorânea, 10", "14:00", comp)
deve_bloquear("enviar pedido sem itens", comp.realizar_pedido, p, m1)
p.adicionar_item(ItemPedido(1, sururu, 30.0))
deve_bloquear("mesmo produto duas vezes", p.adicionar_item, ItemPedido(1, sururu, 30.0))
deve_bloquear("enviar para marisqueira errada", comp.realizar_pedido, p, m2)
deve_bloquear("aceitar pedido que não foi enviado", m1.aceitar_pedido, p)
comp.realizar_pedido(p, m1)
conferir("sem valor mínimo: total = 30 kg x R$ 30,00 = R$ 900,00", p.total() == 900.0)
deve_bloquear("entrega antes do aceite", m1.atualizar_status_entrega, p, "em curso")
m1.aceitar_pedido(p)
conferir("estoque debitado (100 - 30 = 70 kg)", sururu.get_quantidade_disponivel() == 70)
deve_bloquear("status 'banana'", m1.atualizar_status_entrega, p, "banana")
deve_bloquear("pular para 'finalizado'", m1.atualizar_status_entrega, p, "finalizado")
deve_passar("em curso", m1.atualizar_status_entrega, p, "em curso")
deve_passar("finalizado", m1.atualizar_status_entrega, p, "finalizado")
deve_bloquear("alterar pedido finalizado", p.adicionar_item, ItemPedido(1, camarao, 25.0))

print("\n=== REJEIÇÃO E AJUSTE ===")
m1, m2, comp, sururu, camarao, ostra = novo_cenario()
p = Pedido(1, "Av Litorânea, 10", "14:00", comp)
p.adicionar_item(ItemPedido(1, sururu, 30.0))
comp.realizar_pedido(p, m1)
m1.solicitar_ajuste(p, "Reduzir para 25 kg")
deve_bloquear("aceitar sem a compradora reenviar", m1.aceitar_pedido, p)
p.remover_item(sururu)
p.adicionar_item(ItemPedido(1, sururu, 25.0))
p.reenviar()
m1.aceitar_pedido(p)
conferir("pedido ajustado aceito, estoque 75 kg", sururu.get_quantidade_disponivel() == 75)
p2 = Pedido(2, "Av Litorânea, 10", "14:00", comp)
p2.adicionar_item(ItemPedido(2, camarao, 25.0))
comp.realizar_pedido(p2, m1)
m1.rejeitar_pedido(p2)
conferir("rejeição não mexe no estoque", camarao.get_quantidade_disponivel() == 50)
deve_bloquear("aceitar pedido rejeitado", m1.aceitar_pedido, p2)
p3 = Pedido(3, "Av Litorânea, 10", "14:00", comp)
p3.adicionar_item(ItemPedido(3, camarao, 50.0))
comp.realizar_pedido(p3, m1)
m1.alterar_quantidade(camarao, 30)
deve_bloquear("aceitar quando o estoque diminuiu depois", m1.aceitar_pedido, p3)

print("\n=== PREÇO FIXO NA VENDA (RN07) ===")
m1, m2, comp, sururu, camarao, ostra = novo_cenario()
p = Pedido(1, "Av Litorânea, 10", "14:00", comp)
p.adicionar_item(ItemPedido(1, sururu, 30.0))
sururu.preco = 99.0
conferir("pedido mantém R$ 30,00/kg depois da mudança de preço", p.total() == 900.0)

print("\n=== BUSCA, ORDENAÇÃO, COMPARAÇÃO E SITUAÇÃO (RN10, RN11, RN12, RN20) ===")
m1, m2, comp, sururu, camarao, ostra = novo_cenario()
catalogo = m1.produtos + m2.produtos
nomes = []
for x in comp.consultar_produtos(catalogo, categoria="fresco", ordenar_por="menor_preco"):
    nomes.append(x.nome)
conferir("fresco + menor preço = Sururu, Ostra", nomes == ["Sururu Descascado", "Ostra"])
conferir("busca por nome parcial", comp.consultar_produtos(catalogo, nome="CAMAR") == [camarao])
conferir("filtro por localização", comp.consultar_produtos(catalogo, localizacao="Paço do Lumiar - MA") == [ostra])
conferir("filtro por empresa", comp.consultar_produtos(catalogo, empresa="Ilha Azul Mariscos") == [ostra])
conferir("maior preço primeiro", comp.consultar_produtos(catalogo, ordenar_por="maior_preco")[0] == ostra)
entregar_pedido(m1, comp, sururu, 70)
conferir("filtro por avaliação mínima", comp.consultar_produtos(catalogo, avaliacao_minima=4) == [])
entregue = entregar_pedido(m1, comp, camarao, 71)
comp.avaliar_empresa(1, 4, entregue)
conferir("avaliação mínima 4 só traz a Vila Maresia", comp.consultar_produtos(catalogo, avaliacao_minima=4) == [sururu, camarao])
conferir("melhor avaliação primeiro", comp.consultar_produtos(catalogo, ordenar_por="melhor_avaliacao")[-1] == ostra)
deve_bloquear("ordenação inválida", comp.consultar_produtos, catalogo, None, None, None, None, None, "cor")
conferir("comparação entre empresas diferentes", len(comp.comparar_produtos(sururu, ostra)) == 2)
deve_bloquear("comparar produto com ele mesmo", comp.comparar_produtos, sururu, sururu)
conferir("22h = vermelho", m1.situacao(22) == "vermelho")
m1.alterar_quantidade(sururu, 10)
m1.alterar_quantidade(camarao, 10)
conferir("estoque baixo = laranja", m1.situacao(12) == "laranja")
m1.alterar_quantidade(sururu, 100)
conferir("estoque alto = verde", m1.situacao(12) == "verde")
m1.alterar_quantidade(camarao, 24)
m1.alterar_quantidade(sururu, 24)
conferir("nenhum produto com 25 kg ou mais = laranja", m1.situacao(12) == "laranja")

print(f"\n{'TUDO CERTO' if falhas == 0 else str(falhas) + ' TESTE(S) FALHARAM'}")
