class ItemPedido:
    """Entidade associativa entre Pedido e Produto."""

    def __init__(self, id_pedido, produto, quantidade):
        self.id_pedido = id_pedido
        self.produto = produto
        self.id_produto = produto.id_produto
        self.quantidade = quantidade
        self.preco_unitario = produto.preco  # RN07: o preço fica "congelado" no pedido

    def validar_quantidade(self):
        # RN05 / RN15: mínimo de 25 kg para cada produto
        if self.quantidade < 25:
            raise ValueError(f"{self.produto.nome}: a quantidade mínima é de 25 kg (pedido: {self.quantidade} kg).")
        return True


class Pedido:
    """Pedido de uma empresa compradora a UMA empresa marisqueira."""

    # Para onde cada status pode ir (fluxo: análise -> aceite/rejeição/ajuste -> preparo -> entrega)
    TRANSICOES = {
        "pendente": ["em preparo", "rejeitado", "ajuste solicitado"],
        "ajuste solicitado": ["pendente", "rejeitado"],
        "em preparo": ["em curso"],
        "em curso": ["finalizado"],
        "rejeitado": [],
        "finalizado": [],
    }

    def __init__(self, id_pedido, endereco_entrega, tempo_entrega, empresa_compradora):
        # RN13: o pedido registra compradora, itens, endereço e tempo de entrega
        if endereco_entrega.strip() == "" or tempo_entrega.strip() == "":
            raise ValueError("Endereço e tempo de entrega são obrigatórios.")
        self.id_pedido = id_pedido
        self.endereco_entrega = endereco_entrega
        self.tempo_entrega = tempo_entrega
        self.empresa_compradora = empresa_compradora
        self.itens = []
        self.empresa_marisqueira = None
        self.ajuste_solicitado = ""
        self.avaliado = False
        self.__status_pedido = "pendente"  # privado: só muda por alterar_status()

    def get_status_pedido(self):
        return self.__status_pedido

    def alterar_status(self, novo_status):
        if novo_status not in self.TRANSICOES[self.__status_pedido]:
            raise ValueError(f"Mudança de status não permitida: '{self.__status_pedido}' -> '{novo_status}'.")
        self.__status_pedido = novo_status

    def adicionar_item(self, item):
        if self.__status_pedido not in ("pendente", "ajuste solicitado"):
            raise ValueError("Este pedido não pode mais ser alterado.")

        # RN05 / RN15: 25 kg mínimos por produto
        item.validar_quantidade()

        # RN14: um pedido não reúne produtos de marisqueiras diferentes
        empresa = item.produto.empresa_origem
        if self.empresa_marisqueira is not None and empresa is not self.empresa_marisqueira:
            raise ValueError("Um pedido não pode reunir produtos de empresas marisqueiras diferentes.")

        for existente in self.itens:
            if existente.produto is item.produto:
                raise ValueError("Este produto já está no pedido.")

        # RN17 / RN18: a quantidade não pode ultrapassar a disponível
        if not item.produto.verificar_disponibilidade(item.quantidade):
            raise ValueError(
                f"Quantidade {item.quantidade} kg indisponível para {item.produto.nome} "
                f"(disponível: {item.produto.get_quantidade_disponivel()} kg)."
            )

        self.itens.append(item)
        self.empresa_marisqueira = empresa

    def remover_item(self, produto):
        if self.__status_pedido not in ("pendente", "ajuste solicitado"):
            raise ValueError("Este pedido não pode mais ser alterado.")
        for item in self.itens:
            if item.produto is produto:
                self.itens.remove(item)
                return
        raise ValueError("Este produto não está no pedido.")

    def verificar_disponibilidade(self):
        """Confere de novo o estoque de todos os itens."""
        if len(self.itens) == 0:
            return False
        for item in self.itens:
            if not item.produto.verificar_disponibilidade(item.quantidade):
                return False
        return True

    def reenviar(self):
        """A compradora devolve o pedido ajustado para nova análise."""
        if len(self.itens) == 0:
            raise ValueError("O pedido precisa ter ao menos um item.")
        self.alterar_status("pendente")
        self.ajuste_solicitado = ""

    def descrever(self):
        return f"Pedido {self.id_pedido} [{self.__status_pedido}] - {len(self.itens)} item(ns) - R$ {self.total():.2f}"

    def total(self):
        # RN16: não existe valor mínimo; aqui só calculamos o total
        soma = 0
        for item in self.itens:
            soma += item.quantidade * item.preco_unitario
        return soma
