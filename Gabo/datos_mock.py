import pandas as pd
import random

def generar_base_datos():
    # Estructura simple: precio_paquete es EXACTAMENTE lo que cuesta esa bolsa/lata.
    alimentos = [
        # CARBOS FUERTES
        {"nombre": "Arroz Agulha", "etiqueta": "Carbo_Fuerte", "p": 2, "c": 78, "g": 1, "kcal": 350, "tamano_g": 1000, "precio_paquete": 1.15},
        {"nombre": "Massa Esparguete", "etiqueta": "Carbo_Fuerte", "p": 12, "c": 72, "g": 1.5, "kcal": 360, "tamano_g": 500, "precio_paquete": 0.85},
        {"nombre": "Batata Branca", "etiqueta": "Carbo_Fuerte", "p": 2, "c": 17, "g": 0.1, "kcal": 77, "tamano_g": 2000, "precio_paquete": 1.50},
        {"nombre": "Lentilhas", "etiqueta": "Carbo_Fuerte", "p": 24, "c": 60, "g": 1, "kcal": 350, "tamano_g": 500, "precio_paquete": 1.30},
        
        # PROTES FUERTES
        {"nombre": "Peito de Frango", "etiqueta": "Prot_Fuerte", "p": 23, "c": 0, "g": 1.5, "kcal": 110, "tamano_g": 1000, "precio_paquete": 6.00},
        {"nombre": "Atum Posta (Pack 3)", "etiqueta": "Prot_Fuerte", "p": 25, "c": 0, "g": 1, "kcal": 110, "tamano_g": 300, "precio_paquete": 2.50},
        
        # DESAYUNO
        {"nombre": "Aveia Flocos", "etiqueta": "Carbo_Desayuno", "p": 13, "c": 60, "g": 6, "kcal": 370, "tamano_g": 500, "precio_paquete": 1.20},
        {"nombre": "Pao de Forma", "etiqueta": "Carbo_Desayuno", "p": 9, "c": 45, "g": 3, "kcal": 250, "tamano_g": 600, "precio_paquete": 1.40},
        {"nombre": "Ovos M (Dúzia)", "etiqueta": "Prot_Desayuno", "p": 13, "c": 1, "g": 11, "kcal": 155, "tamano_g": 600, "precio_paquete": 2.20},
        {"nombre": "Leite Meio Gordo", "etiqueta": "Prot_Desayuno", "p": 3.3, "c": 4.8, "g": 1.5, "kcal": 47, "tamano_g": 1000, "precio_paquete": 0.85},
        
        # EXTRAS HUMANOS
        {"nombre": "Bananas", "etiqueta": "Extra_Fruta", "p": 1, "c": 23, "g": 0.3, "kcal": 89, "tamano_g": 1000, "precio_paquete": 1.10}
    ]
    
    supermercados = ["Continente", "Pingo Doce"]
    datos = []

    for alimento in alimentos:
        for superm in supermercados:
            # Añade una pequeña variación de céntimos para que los supermercados compitan
            variacion_competencia = random.uniform(0.95, 1.05)
            precio_final = round(alimento["precio_paquete"] * variacion_competencia, 2)
            
            datos.append({
                "Nombre_Etiqueta": f"{alimento['nombre']} {superm[:3]}",
                "Nombre_Base": alimento['nombre'],
                "Supermercado": superm,
                "Etiqueta_Comida": alimento['etiqueta'],
                "Tamano_Paquete_g": alimento['tamano_g'],
                "Precio_Euros": precio_final,
                "Proteina_100g": alimento['p'], 
                "Carbos_100g": alimento['c'], 
                "Grasas_100g": alimento['g'], 
                "Calorias_100g": alimento['kcal']
            })

    pd.DataFrame(datos).to_csv("supermercados_db.csv", index=False)
    print("✅ Base de datos a prueba de errores matemáticos creada.")

if __name__ == "__main__":
    generar_base_datos()