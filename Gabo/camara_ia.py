import random

def analizar_imagen_mock(imagen_bytes):
    """
    Simula la respuesta de la API de OpenAI GPT-4 Vision.
    En el hackathon final, aquí irá tu código real de OpenAI (requests.post).
    """
    # Para la demo, elegimos un "pecado" al azar
    comidas_trampa = [
        {"nombre": "Pizza Pepperoni (3 porciones)", "kcal": 850, "macros": {"p": 35, "c": 90, "g": 38}},
        {"nombre": "Hamburguesa con Queso y Papas", "kcal": 1100, "macros": {"p": 40, "c": 120, "g": 55}},
        {"nombre": "Helado de Chocolate (Copa grande)", "kcal": 450, "macros": {"p": 8, "c": 60, "g": 20}}
    ]
    
    detectado = random.choice(comidas_trampa)
    return detectado

def recalcular_nutricion(exceso_kcal, dias_malos_consecutivos):
    """
    Toma decisiones basadas en el comportamiento del usuario.
    Retorna un diccionario con el plan de acción.
    """
    plan_accion = {
        "cambiar_lista_compras": False,
        "mensaje_coach": "",
        "sugerencia_cardio": None,
        "ajuste_diario": 0
    }

    # REGLA 1: Exceso Crónico (Se portó mal toda la semana)
    if dias_malos_consecutivos >= 7:
        plan_accion["cambiar_lista_compras"] = True
        plan_accion["mensaje_coach"] = "🚨 He notado que esta semana ha sido difícil mantener el plan. ¡No pasa nada! Vamos a generar una NUEVA lista de compras más saciante y estricta para la próxima semana."
        return plan_accion

    # REGLA 2: Exceso Fuerte (Ej: Pizza entera, +800 kcal)
    if exceso_kcal >= 800:
        plan_accion["mensaje_coach"] = "🍕 ¡Esa comida se veía increíble! Te pasaste un poco, pero tu lista de compras semanal sigue intacta. Para compensar, te propongo un trato:"
        plan_accion["sugerencia_cardio"] = f"Corre o haz bici durante 45 minutos mañana para quemar ~400 kcal."
        plan_accion["ajuste_diario"] = -200 # Le restamos 200 kcal a la comida de mañana y pasado
        return plan_accion

    # REGLA 3: Exceso Leve (Ej: Un helado, < 500 kcal)
    else:
        plan_accion["mensaje_coach"] = "🍦 Un gustito no hace daño a nadie. La lista de compras no se toca."
        plan_accion["sugerencia_cardio"] = "Da un paseo de 20 minutos extra hoy."
        plan_accion["ajuste_diario"] = -100 # Pequeño ajuste en la cena de hoy
        return plan_accion