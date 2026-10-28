from empresa import EmpresaMarisqueira, EmpresaCompradora
from produto import Produto
from pedido import Pedido, ItemPedido

print("--- SISTEMA MARISQUEIRAS DA ILHA ---")

# 1. Empresas (polimorfismo: cada uma se descreve do seu jeito)
marisqueira = EmpresaMarisqueira("11.111.111/0001-11", "Vila Maresia Mariscos", "Raposa - MA")
outra = EmpresaMarisqueira("33.333.333/0001-33", "Ilha Azul Mariscos", "Paço do Lumiar - MA")
comprador = EmpresaCompradora("22.222.222/0001-22", "Restaurante Sabor do Mar", "São Luís - MA")
for empresa in (marisqueira, outra, comprador):
    print(empresa.descrever())

# 2. Produtos
sururu = Produto(1, "Sururu Descascado", "fresco", 30.0, 100.0, marisqueira)
camarao = Produto(2, "Camarão Seco", "congelado", 45.0, 50.0, marisqueira)
ostra = Produto(3, "Ostra", "fresco", 60.0, 80.0, outra)
marisqueira.cadastrar_produto(sururu)
marisqueira.cadastrar_produto(camarao)
outra.cadastrar_produto(ostra)
catalogo = marisqueira.produtos + outra.produtos

# 3. Consulta
print("\nProdutos frescos, do menor para o maior preço:")
for p in comprador.consultar_produtos(catalogo, categoria="fresco", ordenar_por="menor_preco"):
    print("  ", p.descrever())

# 4. Pedido com dois produtos da mesma marisqueira
pedido = Pedido(101, "Av Litorânea, 10", "14:00", comprador)
pedido.adicionar_item(ItemPedido(101, sururu, 30.0))
pedido.adicionar_item(ItemPedido(101, camarao, 25.0))
print(f"\nTotal do pedido: R$ {pedido.total():.2f}")
print(comprador.realizar_pedido(pedido, marisqueira))

# 5. Aceite, entrega e avaliação
print(marisqueira.aceitar_pedido(pedido))
print(marisqueira.atualizar_status_entrega(pedido, "em curso"))
print(marisqueira.atualizar_status_entrega(pedido, "finalizado"))
print(comprador.avaliar_empresa(1, 5, pedido))
print(marisqueira.descrever())

# 6. Uma regra violada, tratada com try/except
try:
    outro = Pedido(102, "Av Litorânea, 10", "16:00", comprador)
    outro.adicionar_item(ItemPedido(102, ostra, 10.0))
except ValueError as erro:
    print(f"\nPedido bloqueado: {erro}")
