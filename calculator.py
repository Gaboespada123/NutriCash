from models import UserProfile

def calculate_user_macros(user: UserProfile) -> UserProfile:
    """
    Motor matemático do NutriCash.
    Calcula as necessidades calóricas e os macronutrientes do utilizador
    com base na equação de Mifflin-St Jeor, nível de atividade e objetivos.
    """
    
    # 1. Calcular a Taxa Metabólica Basal (TMB) e definir Mínimos de Segurança
    gender_normalized = user.gender.lower()
    if gender_normalized in ['masculino', 'm', 'homem']:
        tmb = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) + 5
        min_calories = 1500
    else: 
        # Assumimos feminino por defeito para garantir a regra de segurança dos 1200 kcal
        tmb = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) - 161
        min_calories = 1200
        
    # 2. Aplicar o multiplicador de atividade
    activity_multipliers = {
        'sedentario': 1.2,
        'moderado': 1.55,
        'ativo': 1.725
    }
    # Normalizamos o texto para evitar erros do utilizador (ex: "Sedentário" vs "sedentario")
    activity_key = user.activity_level.lower().replace('á', 'a').strip()
    multiplier = activity_multipliers.get(activity_key, 1.2) # Sedentário por segurança se não encontrar
    
    tdee = tmb * multiplier # Total Daily Energy Expenditure (Gasto Energético Total)
    
    # 3. Ajustar calorias com base no objetivo
    goal_adjustments = {
        'perder_peso': -500,
        'manter': 0,
        'ganhar_massa': 300
    }
    goal_key = user.goal.lower().replace(' ', '_').strip()
    adjustment = goal_adjustments.get(goal_key, 0)
    
    target_cals = tdee + adjustment
    
    # 4. Regra de Segurança CRÍTICA (Empatia e Saúde)
    # Se o valor calculado for menor que o limite biológico saudável, forçamos o mínimo.
    target_cals = max(target_cals, min_calories)
    
    # 5. Calcular Macros
    # Proteína: 2.2g por kg de peso corporal
    protein_g = 2.2 * user.weight
    protein_cals = protein_g * 4
    
    # Gordura: 25% das calorias totais
    fat_cals = target_cals * 0.25
    fat_g = fat_cals / 9
    
    # Hidratos: O que sobrar das calorias
    remaining_cals = target_cals - protein_cals - fat_cals
    remaining_cals = max(remaining_cals, 0) # Previne hidratos negativos em dietas muito restritas
    carbs_g = remaining_cals / 4
    
    # 6. Atualizar o objeto utilizador (arredondamos para números inteiros para ser user-friendly)
    user.target_calories = round(target_cals)
    user.target_protein = round(protein_g)
    user.target_fats = round(fat_g)
    user.target_carbs = round(carbs_g)
    
    return user