import pandas as pd
import math
import json
import os
import google.generativeai as genai


ARCHIVO_DESPENSA = "despensa.json"
ARCHIVO_USUARIOS = "usuarios_db.json"
genai.configure(api_key="AIzaSyD6Je2Ye6V5quJWZYq9SrdhU_G3IR-uCMY")


def verificar_usuario(usuario, contraseña):
    if not os.path.exists(ARCHIVO_USUARIOS):
        return False
    with open(ARCHIVO_USUARIOS, 'r') as file:
        db = json.load(file)
    # Compara el usuario y la contraseña (en producción esto iría encriptado)
    return db.get(usuario) == contraseña

def registrar_usuario(usuario, contraseña):
    db = {}
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'r') as file:
            db = json.load(file)
    if usuario in db:
        return False # El usuario ya existe
    db[usuario] = contraseña
    with open(ARCHIVO_USUARIOS, 'w') as file:
        json.dump(db, file)
    return True

def cargar_despensa():
    if os.path.exists(ARCHIVO_DESPENSA):
        with open(ARCHIVO_DESPENSA, 'r') as file:
            return json.load(file)
    return {}

def guardar_despensa(despensa):
    with open(ARCHIVO_DESPENSA, 'w') as file:
        json.dump(despensa, file, indent=4)

def optimizar_cesta(df, macros_diarios, presupuesto_semanal, supermercado_exclusivo=None):
    if supermercado_exclusivo:
        df = df[df['Supermercado'] == supermercado_exclusivo].copy()

    despensa_actual = cargar_despensa()
    nueva_despensa = despensa_actual.copy()
    
    lista_compras = []
    costo_total = 0.0
    
    macros_desayuno = {k: v * 0.3 * 7 for k, v in macros_diarios.items()} 
    macros_fuerte = {k: v * 0.7 * 7 for k, v in macros_diarios.items()}

    necesidades_semana = {}

    # 1. DEFINIMOS LA FUNCIÓN
    def repartir_macros(etiqueta, df_fuente, meta_macro, tipo_macro, cantidad_items, pesos_porcentaje=None):
        limites_humanos = {
            "Leite Meio Gordo": 2000, "Aveia Flocos": 500, "Pao de Forma": 600,
            "Ovos M (Dúzia)": 600, "Batata Branca": 2000, "Peito de Frango": 1500,
            "Massa Esparguete": 500
        }

        opciones = df_fuente[df_fuente['Etiqueta_Comida'] == etiqueta].drop_duplicates(subset=['Nombre_Base']).head(cantidad_items)
        if opciones.empty: return
        
        if not pesos_porcentaje or len(pesos_porcentaje) != len(opciones):
            pesos_porcentaje = [1.0 / len(opciones)] * len(opciones)
            
        for i, (_, fila) in enumerate(opciones.iterrows()):
            macro_asignado = meta_macro * pesos_porcentaje[i]
            gramos = (macro_asignado / fila[f'{tipo_macro}_100g']) * 100
            nombre = fila['Nombre_Base']
            
            if nombre in limites_humanos and gramos > limites_humanos[nombre]:
                gramos = limites_humanos[nombre] 
                
            necesidades_semana[nombre] = necesidades_semana.get(nombre, 0) + gramos

    # 2. ¡LLAMAMOS A LA FUNCIÓN! (Esto era lo que faltaba)
    # Aquí es donde le damos la ESTRUCTURA de una dieta real
    repartir_macros('Prot_Desayuno', df, macros_desayuno['proteina'], 'Proteina', 2, [0.6, 0.4]) 
    repartir_macros('Carbo_Desayuno', df, macros_desayuno['carbos'], 'Carbos', 2, [0.7, 0.3])    
    repartir_macros('Prot_Fuerte', df, macros_fuerte['proteina'], 'Proteina', 2, [0.7, 0.3])     
    repartir_macros('Carbo_Fuerte', df, macros_fuerte['carbos'], 'Carbos', 3, [0.6, 0.2, 0.2])        
    
    # 3. Extras humanos
    frutas = df[df['Etiqueta_Comida'] == 'Extra_Fruta'].drop_duplicates(subset=['Nombre_Base']).head(1)
    for _, fila in frutas.iterrows():
        necesidades_semana[fila['Nombre_Base']] = 1000 

    # 4. CÁLCULO DE PAQUETES Y PRECIOS
    for nombre_base, gramos_necesarios in necesidades_semana.items():
        gramos_en_casa = despensa_actual.get(nombre_base, 0)
        gramos_a_comprar = max(0, gramos_necesarios - gramos_en_casa)
        
        if gramos_en_casa >= gramos_necesarios:
            nueva_despensa[nombre_base] -= gramos_necesarios
            continue
        else:
            nueva_despensa[nombre_base] = 0

        if gramos_a_comprar > 0:
            opciones_paquetes = df[df['Nombre_Base'] == nombre_base].copy()
            mejor_opcion = None
            menor_costo = float('inf')
            
            for _, paquete in opciones_paquetes.iterrows():
                cantidad_paquetes = math.ceil(gramos_a_comprar / paquete['Tamano_Paquete_g'])
                costo_opcion = cantidad_paquetes * paquete['Precio_Euros']
                
                if costo_opcion < menor_costo:
                    menor_costo = costo_opcion
                    mejor_opcion = {
                        "Producto": paquete['Nombre_Etiqueta'], "Tienda": paquete['Supermercado'],
                        "Cantidad": f"{cantidad_paquetes} paq.", "Precio (€)": round(costo_opcion, 2),
                        "Nombre_Base": nombre_base, "Gramos_Comprados": cantidad_paquetes * paquete['Tamano_Paquete_g']
                    }
            
            if mejor_opcion:
                lista_compras.append(mejor_opcion)
                costo_total += mejor_opcion['Precio (€)']
                sobra = mejor_opcion['Gramos_Comprados'] - gramos_a_comprar
                nueva_despensa[nombre_base] = sobra
    
    return lista_compras, round(costo_total, 2), nueva_despensa

def generar_opciones_google_flights(macros_diarios, presupuesto_semanal):
    try:
        df = pd.read_csv("supermercados_db.csv")
    except:
        return None, "Error: Corre datos_mock.py primero."

    opciones = {}
    
    # 1. Ruta Mix
    ticket_mix, costo_mix, despensa_mix = optimizar_cesta(df, macros_diarios, presupuesto_semanal)
    opciones['Ruta Óptima (Mix)'] = {"ticket": ticket_mix, "costo": costo_mix, "despensa_resultante": despensa_mix}

    # 2. Rutas Monomercado
    for superm in df['Supermercado'].unique():
        t_mono, c_mono, d_mono = optimizar_cesta(df, macros_diarios, presupuesto_semanal, supermercado_exclusivo=superm)
        opciones[f'Solo {superm}'] = {"ticket": t_mono, "costo": c_mono, "despensa_resultante": d_mono}

    return opciones, "Éxito"

def generar_recetas_ia(lista_compras):
    """
    Se conecta a Gemini para generar recetas reales y creativas.
    """
    ingredientes = [item['Nombre_Base'] for item in lista_compras]
    ingredientes_str = ", ".join(ingredientes)
    
    prompt = f"""
    Eres el Chef IA de NutriCash. Tu objetivo es ayudar al usuario a cocinar con presupuesto limitado.
    El usuario acaba de comprar estos ingredientes: {ingredientes_str}.
    Asume que en casa tiene sal, pimienta, ajo y aceite. 
    Escribe 2 recetas breves, deliciosas y muy fáciles de hacer. Usa un tono animado y emojis.
    """
    
    try:
        # Usamos el modelo rápido y eficiente
        modelo = genai.GenerativeModel('gemini-1.5-flash')
        respuesta = modelo.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"Ups, el Chef IA está descansando. Error: {e}"