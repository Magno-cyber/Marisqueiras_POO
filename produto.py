class Produto:
    """Marisco vendido por kg. Fresco e congelado são produtos diferentes (RN06)."""

    def __init__(self, id_produto, nome, categoria, preco, quantidade_disponivel, empresa_origem, fotografia=None):
        if nome.strip() == "":
            raise ValueError("O nome do produto é obrigatório.")
        if categoria not in ("fresco", "congelado"):
            raise ValueError("A categoria deve ser 'fresco' ou 'congelado'.")
        if preco <= 0:
            raise ValueError("O preço deve ser maior que zero.")
        if quantidade_disponivel < 25:
            raise ValueError("O cadastro exige no mínimo 25 kg de quantidade disponível.")

        self.id_produto = id_produto
        self.nome = nome
        self.categoria = categoria
        self.preco = preco
        self.fotografia = fotografia  # opcional
        self.empresa_origem = empresa_origem
        # Encapsulamento: o estoque só muda pelos métodos desta classe (os dois _ _ deixam o atributo privado)
        self.__quantidade_disponivel = quantidade_disponivel

    def get_quantidade_disponivel(self):
        return self.__quantidade_disponivel

    def get_status(self):
        # RN09: com estoque zero o produto continua cadastrado, mas aparece como indisponível
        if self.__quantidade_disponivel == 0:
            return "indisponível"
        return "disponível"

    def atualizar_quantidade(self, nova_quantidade):
        # RN08: a empresa pode alterar a quantidade a qualquer momento
        if nova_quantidade < 0:
            raise ValueError("A quantidade não pode ser negativa.")
        self.__quantidade_disponivel = nova_quantidade

    def verificar_disponibilidade(self, quantidade_solicitada):
        # RN17: a quantidade solicitada é limitada pelo estoque
        return self.__quantidade_disponivel >= quantidade_solicitada

    def baixar_estoque(self, quantidade):
        self.__quantidade_disponivel -= quantidade

    def descrever(self):
        return f"{self.nome} [{self.categoria}] R$ {self.preco:.2f}/kg - {self.__quantidade_disponivel} kg ({self.get_status()}) - {self.empresa_origem.nome}"
