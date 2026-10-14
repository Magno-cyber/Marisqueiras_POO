from typing import List, Optional

# ==========================================
# SUPERCLASSE
# ==========================================
class Empresa:
    def __init__(self, nome: str, localizacao: str):
        self.nome = nome
        self.localizacao = localizacao


# ==========================================
# CLASSES DERIVADAS
# ==========================================
class EmpresaMarisqueira(Empresa):
    def __init__(self, id_empresa_marisqueira: str, nome: str, localizacao: str):
        super().__init__(nome, localizacao)
        self.id_empresa_marisqueira = id_empresa_marisqueira # CNPJ
        self.produtos: List['Produto'] = []
        self.pedidos: List['Pedido'] = []

    def cadastrar_produto(self, produto: 'Produto'):
        self.produtos.append(produto)
        print(f"[Sistema] Produto '{produto.nome}' cadastrado pela marisqueira {self.nome}.")

    def alterar_quantidade(self, produto: 'Produto', nova_quantidade: float):
        # A pessoa responsável altera a quantidade disponível (RN08)
        if produto in self.produtos:
            produto.atualizar_quantidade(nova_quantidade)

    def receber_pedido(self, pedido: 'Pedido'):
        self.pedidos.append(pedido)
        print(f"[Marisqueira {self.nome}] Recebeu o pedido {pedido.id_pedido} para análise.")

    def aceitar_pedido(self, pedido: 'Pedido'):
        pedido.status_pedido = "em preparo"
        print(f"[Marisqueira {self.nome}] Pedido {pedido.id_pedido} aceito. Status: {pedido.status_pedido}.")

    def rejeitar_pedido(self, pedido: 'Pedido'):
        pedido.status_pedido = "rejeitado"
        print(f"[Marisqueira {self.nome}] Pedido {pedido.id_pedido} rejeitado.")

    def solicitar_ajuste(self, pedido: 'Pedido', mensagem: str):
        print(f"[Marisqueira {self.nome}] Solicitou ajuste no pedido {pedido.id_pedido}: {mensagem}")

    def atualizar_status_entrega(self, pedido: 'Pedido', novo_status: str):
        # Status permitidos pelo doc: em preparo, em curso, finalizado
        status_permitidos = ["em preparo", "em curso", "finalizado"]
        if novo_status in status_permitidos:
            pedido.status_pedido = novo_status
            print(f"[Entrega] Status do pedido {pedido.id_pedido} atualizado para: {novo_status}")
        else:
            print(f"[Erro] Status '{novo_status}' inválido.")


class EmpresaCompradora(Empresa):
    def __init__(self, id_empresa_compradora: str, nome: str, localizacao: str):
        super().__init__(nome, localizacao)
        self.id_empresa_compradora = id_empresa_compradora # CNPJ

    def consultar_produtos(self, catalogo: List['Produto'], filtro_categoria: str = None) -> List['Produto']:
        # Busca com possibilidade de filtro por categoria (RN10)
        resultados = [p for p in catalogo if filtro_categoria is None or p.categoria == filtro_categoria]
        print(f"[Comprador {self.nome}] Consultou produtos. Encontrados: {len(resultados)}.")
        return resultados

    def comparar_produtos(self, produto1: 'Produto', produto2: 'Produto'):
        print(f"[Comparação] {produto1.nome} (R${produto1.preco}/kg) | {produto2.nome} (R${produto2.preco}/kg)")

    def realizar_pedido(self, pedido: 'Pedido'):
        # Verifica indisponibilidade antes de processar (RN18)
        if pedido.verificar_disponibilidade():
            print(f"[Comprador {self.nome}] Realizando pedido {pedido.id_pedido}...")
            if pedido.empresa_marisqueira:
                pedido.empresa_marisqueira.receber_pedido(pedido)
        else:
            print(f"[Erro] Pedido {pedido.id_pedido} cancelado: Quantidade solicitada maior que a disponível.")

    def avaliar_empresa(self, empresa: EmpresaMarisqueira, nota: int) -> 'Avaliacao':
        # Instancia e registra a avaliação após a compra (RN21)
        nova_avaliacao = Avaliacao(id_avaliacao=len(empresa.pedidos) + 1, nota=nota)
        nova_avaliacao.registrar_nota(nota)
        return nova_avaliacao


# ==========================================
# CLASSES DE NEGÓCIO
# ==========================================
class Produto:
    def __init__(self, id_produto: int, nome: str, categoria: str, preco: float, 
                 quantidade_disponivel: float, empresa_marisqueira: EmpresaMarisqueira, fotografia: str = None):
        self.id_produto = id_produto
        self.nome = nome
        self.categoria = categoria # 'fresco' ou 'congelado' (RN06)
        self.preco = preco
        self.quantidade_disponivel = quantidade_disponivel
        self.fotografia = fotografia
        self.empresa_marisqueira = empresa_marisqueira

    def atualizar_quantidade(self, nova_quantidade: float):
        self.quantidade_disponivel = nova_quantidade
        # Regra: Estoque a zero permanece cadastrado como indisponível (RN09)
        if self.quantidade_disponivel <= 0:
            print(f"[Estoque] Produto '{self.nome}' chegou a 0kg. Status: Indisponível.")

    def verificar_disponibilidade(self, quantidade_solicitada: float) -> bool:
        # Garante que não solicite mais do que tem (RN17, RN18)
        return quantidade_solicitada <= self.quantidade_disponivel


class Pedido:
    def __init__(self, id_pedido: int, endereco_entrega: str, tempo_entrega: str, empresa_compradora: EmpresaCompradora):
        self.id_pedido = id_pedido
        self.endereco_entrega = endereco_entrega
        self.tempo_entrega = tempo_entrega
        self.status_pedido = "criado" # em preparo, em curso, finalizado
        self.empresa_compradora = empresa_compradora
        self.empresa_marisqueira: Optional[EmpresaMarisqueira] = None
        self.itens: List['ItemPedido'] = []

    def adicionar_item(self, item: 'ItemPedido'):
        # Valida regra de 25kg mínimos (RN05, RN15)
        if not item.validar_quantidade():
            print(f"[Erro] Item {item.produto.nome} não atingiu o mínimo de 25kg.")
            return

        # Valida regra de empresas diferentes (RN14)
        if self.empresa_marisqueira is None:
            self.empresa_marisqueira = item.produto.empresa_marisqueira
        elif self.empresa_marisqueira != item.produto.empresa_marisqueira:
            print(f"[Erro] Um pedido não pode reunir produtos de marisqueiras diferentes.")
            return
        
        self.itens.append(item)
        print(f"[Pedido {self.id_pedido}] Adicionado: {item.quantidade}kg de {item.produto.nome}.")

    def verificar_disponibilidade(self) -> bool:
        # Delega a verificação de disponibilidade para cada produto do pedido
        for item in self.itens:
            if not item.produto.verificar_disponibilidade(item.quantidade):
                return False
        return True


class ItemPedido:
    def __init__(self, pedido: Pedido, produto: Produto, quantidade: float):
        self.id_pedido = pedido.id_pedido
        self.id_produto = produto.id_produto
        self.pedido = pedido
        self.produto = produto
        self.quantidade = quantidade

    def validar_quantidade(self) -> bool:
        # A quantidade mínima de comercialização é de 25 kg (RN05)
        return self.quantidade >= 25.0


class Avaliacao:
    def __init__(self, id_avaliacao: int, nota: int):
        self.id_avaliacao = id_avaliacao
        self.nota = nota

    def registrar_nota(self, nota: int):
        # Nota de 1 a 5 estrelas (RN21)
        if 1 <= nota <= 5:
            self.nota = nota
            print(f"[Avaliação] Nota registrada com sucesso: {'⭐' * self.nota}")
        else:
            print(f"[Erro] A nota deve estar entre 1 e 5 estrelas.")


# ==========================================
# EXECUÇÃO DO FLUXO (TESTES)
# ==========================================
if __name__ == "__main__":
    print("--- INICIANDO SISTEMA MARISQUEIRAS DA ILHA ---\n")

    # 1. Instanciando empresas
    marisqueira_joana = EmpresaMarisqueira("11.111.111/0001-11", "Mariscos Joana", "Vila Maresia")
    marisqueira_maria = EmpresaMarisqueira("33.333.333/0001-33", "Pescados Maria", "Vila Maresia")
    restaurante = EmpresaCompradora("22.222.222/0001-22", "Restaurante Frutos do Mar", "São Luís")

    # 2. Cadastrando produtos (RN06 - fresco e congelado)
    sururu_fresco = Produto(1, "Sururu", "fresco", 35.0, 100.0, marisqueira_joana)
    caranguejo_congelado = Produto(2, "Caranguejo", "congelado", 45.0, 30.0, marisqueira_joana)
    peixe_fresco = Produto(3, "Pescada", "fresco", 25.0, 50.0, marisqueira_maria)
    
    marisqueira_joana.cadastrar_produto(sururu_fresco)
    marisqueira_joana.cadastrar_produto(caranguejo_congelado)
    marisqueira_maria.cadastrar_produto(peixe_fresco)
    print()

    # 3. Comprador consulta e compara produtos
    catalogo = [sururu_fresco, caranguejo_congelado, peixe_fresco]
    restaurante.consultar_produtos(catalogo, filtro_categoria="fresco")
    restaurante.comparar_produtos(sururu_fresco, peixe_fresco)
    print()

    # 4. Criando Pedido (Testando regras de negócio)
    pedido_01 = Pedido(1001, "Av. Litorânea, 100", "Hoje às 14h", restaurante)
    
    # Teste RN05: Quantidade < 25kg (Deve falhar)
    item_invalido_kg = ItemPedido(pedido_01, sururu_fresco, 10.0)
    pedido_01.adicionar_item(item_invalido_kg)

    # Teste RN14: Mesma empresa (Deve passar)
    item_valido = ItemPedido(pedido_01, sururu_fresco, 40.0)
    pedido_01.adicionar_item(item_valido)

    # Teste RN14: Empresa diferente no mesmo pedido (Deve falhar)
    item_outra_empresa = ItemPedido(pedido_01, peixe_fresco, 30.0)
    pedido_01.adicionar_item(item_outra_empresa)
    print()

    # 5. Comprador realiza pedido e Marisqueira processa
    restaurante.realizar_pedido(pedido_01)
    marisqueira_joana.aceitar_pedido(pedido_01)
    
    # 6. Atualização de status de entrega (RN22)
    marisqueira_joana.atualizar_status_entrega(pedido_01, "em curso")
    marisqueira_joana.atualizar_status_entrega(pedido_01, "finalizado")
    print()

    # 7. Baixa no estoque e Avaliação
    marisqueira_joana.alterar_quantidade(sururu_fresco, 60.0) # Vendeu 40kg dos 100kg
    restaurante.avaliar_empresa(marisqueira_joana, 5)