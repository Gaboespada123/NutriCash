from models import UserProfile

def recalculate_route(user: UserProfile, slip_data: dict) -> dict:
    """
    O GPS Nutricional. Calcula a nova rota de macros para os próximos 3 dias,
    diluindo o deslize sem colocar a saúde do utilizador em risco.
    """
    # 1. Extrair os valores do JSON da IA (suportando as chaves da Fase 3)
    # Usamos .get() com valor zero por defeito para evitar erros caso a IA não envie algo
    calorias_excedidas = slip_data.get("calorias_a_ajustar", 0)
    hidratos_excedidos = slip_data.get("hidratos_a_ajustar", 0)
    gordura_excedida = slip_data.get("gordura_a_ajustar", 0)

    # 2. Calcular os cortes diários (diluídos em 3 dias para ser suave)
    corte_calorias = calorias_excedidas / 3
    corte_hidratos = hidratos_excedidos / 3
    corte_gordura = gordura_excedida / 3

    # 3. Aplicar cortes aos alvos originais
    novas_calorias = user.target_calories - corte_calorias
    novos_hidratos = user.target_carbs - corte_hidratos
    novas_gorduras = user.target_fats - corte_gordura
    nova_proteina = user.target_protein  # PROTEÍNA É SAGRADA! NUNCA SE CORTA.

    # 4. O GUARDRAIL CLÍNICO (A nossa regra de ouro de saúde)
    gender_normalized = user.gender.lower()
    if gender_normalized in ['masculino', 'm', 'homem']:
        limite_seguranca = 1500
    else:
        # Feminino por defeito para garantir segurança máxima
        limite_seguranca = 1200

    # Se a nova dieta de compensação for uma dieta de fome, ativamos o travão
    if novas_calorias < limite_seguranca:
        # Descobrimos o máximo que podíamos cortar em segurança
        corte_seguro_permitido = user.target_calories - limite_seguranca
        
        # Se o utilizador já estava a comer no limite, perdoamos o deslize a 100% (não corta nada)
        if corte_seguro_permitido <= 0:
            corte_seguro_permitido = 0
            novas_calorias = user.target_calories
        else:
            # Forçamos as calorias para a linha de segurança
            novas_calorias = limite_seguranca

        # Truque de Senior: Ajustamos os hidratos e gorduras de forma proporcional 
        # para que a matemática dos macros continue a fazer sentido com as novas calorias forçadas.
        if corte_calorias > 0:
            proporcao = corte_seguro_permitido / corte_calorias
        else:
            proporcao = 0
            
        novos_hidratos = user.target_carbs - (corte_hidratos * proporcao)
        novas_gorduras = user.target_fats - (corte_gordura * proporcao)

    # Garantir que nenhum macro fica negativo (por exemplo, se o utilizador comeu hidratos absurdos)
    novos_hidratos = max(0, novos_hidratos)
    novas_gorduras = max(0, novas_gorduras)

    # 5. Formatar a devolução
    return {
        "mensagem_empatica": slip_data.get("mensagem_empatica", "Está tudo bem! Acontece aos melhores. Vamos ajustar a rota sem stress."),
        "novos_macros_diarios": {
            "dias_de_aplicacao": 3,
            "calorias": round(novas_calorias),
            "proteina": round(nova_proteina),
            "hidratos": round(novos_hidratos),
            "gordura": round(novas_gorduras)
        }
    }
