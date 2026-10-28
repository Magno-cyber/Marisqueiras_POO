class Avaliacao:
    """Avaliação de 1 a 5 estrelas dada pela empresa compradora à marisqueira (RN21)."""

    def __init__(self, id_avaliacao, nota):
        self.id_avaliacao = id_avaliacao
        self.nota = nota

    def registrar_nota(self):
        if type(self.nota) is not int or self.nota < 1 or self.nota > 5:
            raise ValueError("A nota deve ser um número inteiro de 1 a 5 estrelas.")
        return f"Avaliação registrada. Nota: {self.nota} estrela(s)."
