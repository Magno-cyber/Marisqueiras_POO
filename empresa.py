from avaliacao import Avaliacao


def preco_do_produto(produto):
    return produto.preco


def avaliacao_do_produto(produto):
    return produto.empresa_origem.media_avaliacoes()


class Empresa:
    """Superclasse: dados comuns das empresas (RN01: o sistema é B2B)."""

    def __init__(self, id_empresa, nome, localizacao):
        self.id_empresa = id_empresa  # CNPJ
        self.nome = nome
        self.localizacao = localizacao

    def descrever(self):
        return f"{self.nome} ({self.localizacao})"


class EmpresaMarisqueira(Empresa):
    """Fornece os produtos e faz a entrega."""

    def __init__(self, id_empresa_marisqueira, nome, localizacao, abertura=8, fechamento=18):
        super().__init__(id_empresa_marisqueira, nome, localizacao)
        self.abertura = abertura      # horário de funcionamento (horas)
        self.fechamento = fechamento
        self.produtos = []            # RN12: só os produtos desta empresa
        self.pedidos = []
        self.avaliacoes = []

    def descrever(self):  # polimorfismo: sobrescreve o método da superclasse
        return f"Marisqueira {self.nome} ({self.localizacao}) - média {self.media_avaliacoes():.1f} estrelas"

    def media_avaliacoes(self):
        if len(self.avaliacoes) == 0:
            return 0.0
        soma = 0
        for avaliacao in self.avaliacoes:
            soma += avaliacao.nota
        return soma / len(self.avaliacoes)

    def cadastrar_produto(self, produto):
        if produto.empresa_origem is not self:
            raise ValueError("Este produto pertence a outra empresa.")
        for p in self.produtos:
            if p.nome.lower() == produto.nome.lower() and p.categoria == produto.categoria:
                raise ValueError("Este produto já está cadastrado nesta categoria.")
        self.produtos.append(produto)

    def alterar_quantidade(self, produto, nova_quantidade):
        if produto not in self.produtos:
            raise ValueError("Só é possível alterar produtos da própria empresa.")
        produto.atualizar_quantidade(nova_quantidade)

    def _conferir_pedido(self, pedido):
        if pedido not in self.pedidos:
            raise ValueError("Este pedido não foi recebido por esta marisqueira.")

    def receber_pedido(self, pedido):
        if len(pedido.itens) == 0:
            raise ValueError("O pedido não possui itens.")
        if pedido.empresa_marisqueira is not self:
            raise ValueError("Este pedido é destinado a outra marisqueira.")
        if pedido.get_status_pedido() != "pendente" or pedido in self.pedidos:
            raise ValueError("Este pedido não pode ser recebido.")
        self.pedidos.append(pedido)

    def aceitar_pedido(self, pedido):
        self._conferir_pedido(pedido)
        if pedido.get_status_pedido() != "pendente":
            raise ValueError("Só é possível aceitar pedidos pendentes.")
        # RN18: se o estoque mudou desde o pedido, não aceita
        if not pedido.verificar_disponibilidade():
            raise ValueError("O estoque mudou e não atende mais a este pedido.")
        for item in pedido.itens:
            item.produto.baixar_estoque(item.quantidade)  # RN09: o estoque pode chegar a zero aqui
        pedido.alterar_status("em preparo")
        return f"Pedido {pedido.id_pedido} aceito e em preparo."

    def rejeitar_pedido(self, pedido):
        self._conferir_pedido(pedido)
        pedido.alterar_status("rejeitado")
        return f"Pedido {pedido.id_pedido} rejeitado."

    def solicitar_ajuste(self, pedido, ajuste):
        self._conferir_pedido(pedido)
        if ajuste.strip() == "":
            raise ValueError("Descreva o ajuste solicitado.")
        pedido.alterar_status("ajuste solicitado")
        pedido.ajuste_solicitado = ajuste
        return f"Ajuste solicitado para o pedido {pedido.id_pedido}: {ajuste}"

    def atualizar_status_entrega(self, pedido, novo_status):
        # RN22: a marisqueira informa o andamento da entrega (sem rastreamento em tempo real)
        self._conferir_pedido(pedido)
        if novo_status not in ("em curso", "finalizado"):
            raise ValueError("Status de entrega inválido. Use 'em curso' ou 'finalizado'.")
        pedido.alterar_status(novo_status)
        return f"Pedido {pedido.id_pedido}: entrega '{novo_status}'."

    def situacao(self, hora_atual):
        # RN20: vermelho = fora do horário, laranja = estoque baixo, verde = disponível
        if hora_atual < self.abertura or hora_atual > self.fechamento:
            return "vermelho"
        # Estoque baixo = nenhum produto com pelo menos 25 kg (o mínimo de venda, RN05)
        for p in self.produtos:
            if p.get_quantidade_disponivel() >= 25:
                return "verde"
        return "laranja"


class EmpresaCompradora(Empresa):
    """Faz as compras."""

    def descrever(self):  # polimorfismo
        return f"Compradora {self.nome} ({self.localizacao})"

    def consultar_produtos(self, catalogo, nome=None, categoria=None, localizacao=None,
                           empresa=None, avaliacao_minima=None, ordenar_por=None):
        # RN10: filtros | RN11: ordenação | produtos sem estoque continuam aparecendo (RN09)
        resultado = []
        for p in catalogo:
            marisqueira = p.empresa_origem
            if nome is not None and nome.lower() not in p.nome.lower():
                continue
            if categoria is not None and p.categoria != categoria:
                continue
            if localizacao is not None and marisqueira.localizacao != localizacao:
                continue
            if empresa is not None and marisqueira.nome != empresa:
                continue
            if avaliacao_minima is not None and marisqueira.media_avaliacoes() < avaliacao_minima:
                continue
            resultado.append(p)

        if ordenar_por == "menor_preco":
            resultado.sort(key=preco_do_produto)
        elif ordenar_por == "maior_preco":
            resultado.sort(key=preco_do_produto, reverse=True)
        elif ordenar_por == "melhor_avaliacao":
            resultado.sort(key=avaliacao_do_produto, reverse=True)
        elif ordenar_por == "proximidade":  # mesma localização da compradora primeiro
            perto = []
            longe = []
            for p in resultado:
                if p.empresa_origem.localizacao == self.localizacao:
                    perto.append(p)
                else:
                    longe.append(p)
            resultado = perto + longe
        elif ordenar_por is not None:
            raise ValueError("Ordenação inválida.")
        return resultado

    def comparar_produtos(self, produto1, produto2):
        if produto1 is produto2:
            raise ValueError("Escolha dois produtos diferentes.")
        comparacao = {}
        for p in (produto1, produto2):
            chave = f"{p.nome} ({p.categoria}) - {p.empresa_origem.nome}"
            comparacao[chave] = f"R$ {p.preco:.2f}/kg, {p.empresa_origem.media_avaliacoes():.1f} estrelas, {p.get_status()}"
        return comparacao

    def realizar_pedido(self, pedido, empresa_marisqueira):
        if pedido.empresa_compradora is not self:
            raise ValueError("Este pedido pertence a outra compradora.")
        empresa_marisqueira.receber_pedido(pedido)
        return f"Pedido {pedido.id_pedido} realizado com sucesso para a marisqueira {empresa_marisqueira.nome}."

    def avaliar_empresa(self, id_avaliacao, nota, pedido):
        # RN21: só depois da compra (entrega finalizada), uma vez por pedido
        if pedido.empresa_compradora is not self:
            raise ValueError("Só é possível avaliar pedidos da própria compradora.")
        if pedido.get_status_pedido() != "finalizado":
            raise ValueError("A avaliação só é permitida após a entrega do pedido.")
        if pedido.avaliado:
            raise ValueError("Este pedido já foi avaliado.")
        avaliacao = Avaliacao(id_avaliacao, nota)
        mensagem = avaliacao.registrar_nota()  # valida a nota (1 a 5)
        pedido.empresa_marisqueira.avaliacoes.append(avaliacao)
        pedido.avaliado = True
        return mensagem
