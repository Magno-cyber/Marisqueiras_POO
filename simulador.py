"""Simulador interativo - Marisqueiras da Ilha.   Rode:  python simulador.py

Você digita os dados e as regras de negócio aceitam ou bloqueiam cada operação.
O menu é dividido por perfil: primeiro cadastre (ou carregue o exemplo), depois
entre como marisqueira ou como compradora.
"""

from empresa import EmpresaCompradora, EmpresaMarisqueira
from pedido import ItemPedido, Pedido
from produto import Produto

marisqueiras = []
compradoras = []
pedidos = []
catalogo = []  # produtos de todas as marisqueiras (o que a compradora enxerga)
contador = {"produto": 1, "pedido": 1, "avaliacao": 1}


# ---------------------------------------------------------------------------
# Entrada de dados
# ---------------------------------------------------------------------------
def ler_numero(texto):
    bruto = input(texto).strip().replace(",", ".")
    try:
        return float(bruto)
    except ValueError:
        raise ValueError("Digite um número válido (ex.: 30 ou 24,5).")


def escolher(lista, nome, mostrar):
    """Mostra a lista numerada e devolve o item escolhido."""
    if len(lista) == 0:
        raise ValueError(f"Nenhum(a) {nome} disponível para esta ação.")
    for posicao, item in enumerate(lista, 1):
        print(f"   {posicao}) {mostrar(item)}")
    bruto = input(f"  Número do(a) {nome}: ").strip()
    if not bruto.isdigit() or int(bruto) < 1 or int(bruto) > len(lista):
        raise ValueError("Escolha inválida.")
    return lista[int(bruto) - 1]


def nome_da_empresa(empresa):
    return empresa.descrever()


def descrever(objeto):
    return objeto.descrever()


# ---------------------------------------------------------------------------
# Cadastros e exemplo
# ---------------------------------------------------------------------------
def novo_produto(marisqueira, nome, categoria, preco, quantidade):
    produto = Produto(contador["produto"], nome, categoria, preco, quantidade, marisqueira)
    marisqueira.cadastrar_produto(produto)  # só conta o id se o cadastro passar
    catalogo.append(produto)
    contador["produto"] += 1
    return produto


def carregar_exemplo():
    maresia = EmpresaMarisqueira("11.111.111/0001-11", "Vila Maresia Mariscos", "Raposa - MA")
    azul = EmpresaMarisqueira("33.333.333/0001-33", "Ilha Azul Mariscos", "Paço do Lumiar - MA")
    marisqueiras.extend([maresia, azul])
    compradoras.append(EmpresaCompradora("22.222.222/0001-22", "Restaurante Sabor do Mar", "São Luís - MA"))
    novo_produto(maresia, "Sururu Descascado", "fresco", 30.0, 100.0)
    novo_produto(maresia, "Camarão Seco", "congelado", 45.0, 50.0)
    novo_produto(azul, "Ostra", "fresco", 60.0, 80.0)
    print("  Exemplo carregado: 2 marisqueiras, 1 compradora, 3 produtos.")


# ---------------------------------------------------------------------------
# Perfil: marisqueira
# ---------------------------------------------------------------------------
MENU_MARISQUEIRA = """
 --- MARISQUEIRA ---
 1) Cadastrar produto            5) Aceitar pedido
 2) Alterar quantidade (estoque) 6) Rejeitar pedido
 3) Ver meus produtos            7) Pedir ajuste
 4) Ver pedidos recebidos        8) Atualizar entrega
 9) Ver minha situação (cor)     0) Voltar
"""


def perfil_marisqueira():
    m = escolher(marisqueiras, "marisqueira", nome_da_empresa)
    print(f"\n  Você entrou como: {m.descrever()}")
    print(MENU_MARISQUEIRA)
    while True:
        opcao = input("[marisqueira] opção (m = menu): ").strip().lower()
        if opcao == "0":
            return
        if opcao == "m":
            print(MENU_MARISQUEIRA)
            continue
        try:
            if opcao == "1":
                produto = novo_produto(m, input("  Nome: "), input("  Categoria (fresco/congelado): "),
                                       ler_numero("  Preço por kg: "), ler_numero("  Quantidade (kg): "))
                print("  OK:", produto.descrever())
            elif opcao == "2":
                produto = escolher(m.produtos, "produto", descrever)
                m.alterar_quantidade(produto, ler_numero("  Nova quantidade (kg): "))
                print("  OK:", produto.descrever())
            elif opcao == "3":
                if len(m.produtos) == 0:
                    print("  (nenhum produto cadastrado)")
                for produto in m.produtos:
                    print("  •", produto.descrever())
            elif opcao == "4":
                if len(m.pedidos) == 0:
                    print("  (nenhum pedido recebido)")
                for pedido in m.pedidos:
                    print("  •", pedido.descrever(), "| comprador:", pedido.empresa_compradora.nome)
            elif opcao == "5":
                print("  OK:", m.aceitar_pedido(escolher(m.pedidos, "pedido", descrever)))
            elif opcao == "6":
                print("  OK:", m.rejeitar_pedido(escolher(m.pedidos, "pedido", descrever)))
            elif opcao == "7":
                pedido = escolher(m.pedidos, "pedido", descrever)
                print("  OK:", m.solicitar_ajuste(pedido, input("  O que precisa ser ajustado: ")))
            elif opcao == "8":
                pedido = escolher(m.pedidos, "pedido", descrever)
                print("  OK:", m.atualizar_status_entrega(pedido, input("  Novo status (em curso/finalizado): ").strip()))
            elif opcao == "9":
                hora = int(ler_numero("  Hora a simular (0 a 23): "))
                print(f"  Situação às {hora}h: {m.situacao(hora)}  (verde = disponível, laranja = estoque baixo, vermelho = fora do horário)")
            else:
                print("  Opção inválida.")
        except ValueError as erro:
            print("  BLOQUEADO:", erro)


# ---------------------------------------------------------------------------
# Perfil: compradora
# ---------------------------------------------------------------------------
MENU_COMPRADORA = """
 --- COMPRADORA ---
 1) Buscar / ordenar produtos     6) Enviar pedido à marisqueira
 2) Comparar dois produtos        7) Reenviar pedido ajustado
 3) Criar pedido                  8) Ver meus pedidos
 4) Adicionar item ao pedido      9) Avaliar marisqueira (1 a 5)
 5) Remover item do pedido        0) Voltar
"""


def pedidos_da(compradora, status=None):
    lista = []
    for p in pedidos:
        if p.empresa_compradora is compradora and (status is None or p.get_status_pedido() in status):
            lista.append(p)
    return lista


def perfil_compradora():
    c = escolher(compradoras, "compradora", nome_da_empresa)
    print(f"\n  Você entrou como: {c.descrever()}")
    print(MENU_COMPRADORA)
    while True:
        opcao = input("[compradora] opção (m = menu): ").strip().lower()
        if opcao == "0":
            return
        if opcao == "m":
            print(MENU_COMPRADORA)
            continue
        try:
            if opcao == "1":
                print("  (deixe em branco para não filtrar)")
                nome = input("  Nome contém: ").strip() or None
                categoria = input("  Categoria (fresco/congelado): ").strip() or None
                localizacao = input("  Localização exata: ").strip() or None
                empresa = input("  Nome exato da marisqueira: ").strip() or None
                minima = input("  Avaliação mínima (0 a 5): ").strip().replace(",", ".")
                minima = ler_numero_ou_none(minima)
                ordem = input("  Ordenar por (menor_preco / maior_preco / melhor_avaliacao / proximidade): ").strip() or None
                resultado = c.consultar_produtos(catalogo, nome, categoria, localizacao, empresa, minima, ordem)
                print(f"  {len(resultado)} resultado(s):")
                for produto in resultado:
                    print("  •", produto.descrever(), f"| {produto.empresa_origem.media_avaliacoes():.1f} estrelas")
            elif opcao == "2":
                print("  Primeiro produto:")
                p1 = escolher(catalogo, "produto", descrever)
                print("  Segundo produto:")
                p2 = escolher(catalogo, "produto", descrever)
                for chave, dados in c.comparar_produtos(p1, p2).items():
                    print(f"  • {chave}: {dados}")
            elif opcao == "3":
                pedido = Pedido(contador["pedido"], input("  Endereço de entrega: "), input("  Tempo de entrega: "), c)
                pedidos.append(pedido)
                contador["pedido"] += 1
                print(f"  OK: Pedido {pedido.id_pedido} criado. Use a opção 4 para adicionar itens.")
            elif opcao == "4":
                pedido = escolher(pedidos_da(c, ["pendente", "ajuste solicitado"]), "pedido", descrever)
                print("  Produto (de qualquer marisqueira - tente misturar para ver a RN14):")
                produto = escolher(catalogo, "produto", descrever)
                pedido.adicionar_item(ItemPedido(pedido.id_pedido, produto, ler_numero("  Quantidade (kg): ")))
                print("  OK:", pedido.descrever())
            elif opcao == "5":
                pedido = escolher(pedidos_da(c, ["pendente", "ajuste solicitado"]), "pedido", descrever)
                produto = escolher([i.produto for i in pedido.itens], "produto a remover", descrever)
                pedido.remover_item(produto)
                print("  OK:", pedido.descrever())
            elif opcao == "6":
                a_enviar = []
                for p in pedidos_da(c, ["pendente"]):
                    if p.empresa_marisqueira is None or p not in p.empresa_marisqueira.pedidos:
                        a_enviar.append(p)
                pedido = escolher(a_enviar, "pedido a enviar", descrever)
                if len(pedido.itens) == 0:
                    raise ValueError("O pedido não possui itens.")
                print("  OK:", c.realizar_pedido(pedido, pedido.empresa_marisqueira))
            elif opcao == "7":
                pedido = escolher(pedidos_da(c, ["ajuste solicitado"]), "pedido com ajuste", descrever)
                print(f"  Ajuste pedido pela marisqueira: {pedido.ajuste_solicitado}")
                pedido.reenviar()
                print(f"  OK: Pedido {pedido.id_pedido} reenviado para nova análise.")
            elif opcao == "8":
                lista = pedidos_da(c)
                if len(lista) == 0:
                    print("  (nenhum pedido)")
                for p in lista:
                    print("  •", p.descrever())
                    for item in p.itens:
                        print(f"       - {item.produto.nome}: {item.quantidade} kg x R$ {item.preco_unitario:.2f}")
                    if p.ajuste_solicitado != "":
                        print("       ajuste pedido:", p.ajuste_solicitado)
            elif opcao == "9":
                print("  (todos os pedidos aparecem de propósito: avaliar um pedido não entregue deve ser bloqueado)")
                pedido = escolher(pedidos_da(c), "pedido a avaliar", descrever)
                bruto = input("  Nota (1 a 5): ").strip()
                try:
                    nota = int(bruto)
                except ValueError:
                    nota = bruto  # o domínio recusa
                print("  OK:", c.avaliar_empresa(contador["avaliacao"], nota, pedido))
                contador["avaliacao"] += 1
            else:
                print("  Opção inválida.")
        except ValueError as erro:
            print("  BLOQUEADO:", erro)


def ler_numero_ou_none(bruto):
    if bruto == "":
        return None
    try:
        return float(bruto)
    except ValueError:
        raise ValueError("A avaliação mínima deve ser um número.")


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------
MENU_PRINCIPAL = """
=========== SIMULADOR - MARISQUEIRAS DA ILHA ===========
 1) Cadastrar marisqueira       4) Entrar como COMPRADORA
 2) Cadastrar compradora        5) Carregar dados de exemplo
 3) Entrar como MARISQUEIRA     6) Ver tudo
 0) Sair
========================================================"""

def principal():
    print(MENU_PRINCIPAL)
    while True:
        opcao = input("\nOpção (m = menu): ").strip().lower()
        if opcao == "0":
            break
        if opcao == "m":
            print(MENU_PRINCIPAL)
            continue
        try:
            if opcao == "1":
                empresa = EmpresaMarisqueira(input("  CNPJ: "), input("  Nome: "), input("  Localização: "))
                marisqueiras.append(empresa)
                print("  OK:", empresa.descrever())
            elif opcao == "2":
                empresa = EmpresaCompradora(input("  CNPJ: "), input("  Nome: "), input("  Localização: "))
                compradoras.append(empresa)
                print("  OK:", empresa.descrever())
            elif opcao == "3":
                perfil_marisqueira()
                print(MENU_PRINCIPAL)
            elif opcao == "4":
                perfil_compradora()
                print(MENU_PRINCIPAL)
            elif opcao == "5":
                carregar_exemplo()
            elif opcao == "6":
                for lista in (marisqueiras, compradoras, catalogo, pedidos):
                    for item in lista:
                        print("  •", item.descrever())
            else:
                print("  Opção inválida.")
        except ValueError as erro:
            print("  BLOQUEADO:", erro)
    print("\nSimulação encerrada.")


try:
    principal()
except (EOFError, KeyboardInterrupt):
    print("\n\nSimulação encerrada.")
