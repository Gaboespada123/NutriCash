from models import UserProfile

# 1. Base de Dados Simulada (MVP)
MOCK_SUPERMARKET_DB = [
    # PROTEÍNAS
    {"id": 1, "name": "Peito de Frango (Marca Branca)", "category": "Proteína", "price_per_100g": 0.75, "protein_per_100g": 25, "carbs_per_100g": 0, "fats_per_100g": 2},
    {"id": 2, "name": "Peito de Frango Biológico Premium", "category": "Proteína", "price_per_100g": 1.45, "protein_per_100g": 24, "carbs_per_100g": 0, "fats_per_100g": 3},
    {"id": 3, "name": "Atum em Lata (Pack Poupança)", "category": "Proteína", "price_per_100g": 0.90, "protein_per_100g": 22, "carbs_per_100g": 0, "fats_per_100g": 1},
    
    # HIDRATOS
    {"id": 4, "name": "Arroz Agulha (Saco 1kg)", "category": "Hidratos", "price_per_100g": 0.15, "protein_per_100g": 7, "carbs_per_100g": 78, "fats_per_100g": 1},
    {"id": 5, "name": "Quinoa Real Orgânica", "category": "Hidratos", "price_per_100g": 0.85, "protein_per_100g": 14, "carbs_per_100g": 64, "fats_per_100g": 6},
    {"id": 6, "name": "Massa Esparguete (Económica)", "category": "Hidratos", "price_per_100g": 0.12, "protein_per_100g": 12, "carbs_per_100g": 72, "fats_per_100g": 2},

    # GORDURAS
    {"id": 7, "name": "Manteiga de Amendoim Natural", "category": "Gorduras", "price_per_100g": 0.60, "protein_per_100g": 25, "carbs_per_100g": 15, "fats_per_100g": 50},
    {"id": 8, "name": "Abacate Importado (Unidade)", "category": "Gorduras", "price_per_100g": 1.10, "protein_per_100g": 2, "carbs_per_100g": 9, "fats_per_100g": 15},
    {"id": 9, "name": "Azeite Virgem Extra (Marca Branca)", "category": "Gorduras", "price_per_100g": 0.95, "protein_per_100g": 0, "carbs_per_100g": 0, "fats_per_100g": 91},
]

def generate_smart_cart(user: UserProfile) -> dict:
    """
    Gera um carrinho de compras otimizado para o menor preço, 
    garantindo que os macros alvo são atingidos.
    """
    
    # 2. Filtrar as opções mais baratas e mais caras por categoria
    categories = ["Proteína", "Hidratos", "Gorduras"]
    smart_choices = {}
    premium_choices = {}

    for cat in categories:
        items = [i for i in MOCK_SUPERMARKET_DB if i["category"] == cat]
        # Ordenar por preço para encontrar a pechincha e o luxo
        items_sorted = sorted(items, key=lambda x: x["price_per_100g"])
        smart_choices[cat] = items_sorted[0]
        premium_choices[cat] = items_sorted[-1]

    # 3. Calcular Quantidades e Custos (Carrinho Inteligente)
    cart_items = []
    total_cost = 0.0
    
    # Cálculo Simplificado para o MVP: Baseado no nutriente principal da categoria
    # Proteína
    p_item = smart_choices["Proteína"]
    p_qty = (user.target_protein / p_item["protein_per_100g"]) * 100
    p_cost = (p_qty / 100) * p_item["price_per_100g"]
    
    # Hidratos
    h_item = smart_choices["Hidratos"]
    h_qty = (user.target_carbs / h_item["carbs_per_100g"]) * 100
    h_cost = (h_qty / 100) * h_item["price_per_100g"]
    
    # Gorduras
    g_item = smart_choices["Gorduras"]
    g_qty = (user.target_fats / g_item["fats_per_100g"]) * 100
    g_cost = (g_qty / 100) * g_item["price_per_100g"]

    # Montar lista do carrinho inteligente
    for item, qty, cost in [(p_item, p_qty, p_cost), (h_item, h_qty, h_cost), (g_item, g_qty, g_cost)]:
        cart_items.append({
            "produto": item["name"],
            "quantidade_sugerida_g": round(qty),
            "preço_estimado": round(cost, 2)
        })
        total_cost += cost

    # 4. Calcular o custo do "Carrinho Premium" para mostrar a poupança
    premium_total = 0.0
    premium_total += (user.target_protein / premium_choices["Proteína"]["protein_per_100g"]) * premium_choices["Proteína"]["price_per_100g"]
    premium_total += (user.target_carbs / premium_choices["Hidratos"]["carbs_per_100g"]) * premium_choices["Hidratos"]["price_per_100g"]
    premium_total += (user.target_fats / premium_choices["Gorduras"]["fats_per_100g"]) * premium_choices["Gorduras"]["price_per_100g"]

    savings = premium_total - total_cost

    return {
        "carrinho_inteligente": cart_items,
        "custo_total_diario": round(total_cost, 2),
        "poupanca_estimada_diaria": round(savings, 2)
    }

