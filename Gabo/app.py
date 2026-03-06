import streamlit as st
import algoritmo
import pagos
import time 
import coach_ia
import google.generativeai as genai
# Configuración inicial
st.set_page_config(page_title="NutriCash", page_icon="🛒", layout="wide")
genai.configure(api_key="AIzaSyD6Je2Ye6V5quJWZYq9SrdhU_G3IR-uCMY")

# Inicializar variables de sesión globales
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_plan' not in st.session_state:
    st.session_state.user_plan = "Free"
if 'recalculos_usados' not in st.session_state:
    st.session_state.recalculos_usados = 0
if 'macros' not in st.session_state:
    st.session_state.macros = {"calorias": 0, "proteina": 0, "carbos": 0, "grasas": 0}

# --- SISTEMA DE LOGIN FALSO ---
def mostrar_login():
    st.title(" Bienvenido a NutriCash")
    st.markdown("Tu GPS nutricional y financiero.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Iniciar Sesión")
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        plan_elegido = st.radio("Simular entrada como:", ["Free", "Premium"])
        
        if st.button("Entrar"):
            if user and password:
                st.session_state.logged_in = True
                st.session_state.user_plan = plan_elegido
                st.rerun()
            else:
                st.error("Por favor, ingresa credenciales.")

# --- NAVEGACIÓN PRINCIPAL ---
def mostrar_app_principal():
    st.sidebar.title(f" Perfil: {st.session_state.user_plan}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("Navegación", [
        " Mi Perfil y Macros", 
        " Generar Lista de Compras", 
        " Escáner Calc AI (Recalcular)", 
        "Habla con tu Coach Personal de IA",
        " Upgrade a Premium"
    ])

    # ---------------------------------------------------------
    # SECCIÓN 1: CALCULADORA DE MACROS
    # ---------------------------------------------------------
    if menu == " Mi Perfil y Macros":
        st.header("Tus Datos Nutricionales")
        
        with st.expander(" ¿No sabes tus macros? Calcúlalos aquí", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                # Usamos text_input para quitar las flechas y lo convertimos a número
                peso_str = st.text_input("Peso (kg)", placeholder="Ej: 70", value="70")
                edad_str = st.text_input("Edad", placeholder="Ej: 25", value="25")
                
                # Validación de seguridad (por si el usuario escribe letras por error)
                try:
                    peso = float(peso_str)
                    edad = int(edad_str)
                except ValueError:
                    peso, edad = 70.0, 25 
            with col2:
                altura_str = st.text_input("Altura (cm)", placeholder="Ej: 175", value="175")
                try:
                    altura = float(altura_str)
                except ValueError:
                    altura = 175.0
                genero = st.radio("Género", ["Masculino", "Femenino"])
            with col3:
                actividad = st.selectbox("Actividad", ["Sedentario", "Ligera", "Moderada", "Intensa"])
                objetivo = st.selectbox("Objetivo", ["Perder Grasa", "Mantener Peso", "Ganar Músculo"])
                
            if st.button("Calcular Mis Macros"):
                # Fórmula Mifflin-St Jeor (Aproximación simplificada)
                tmb = (10 * peso) + (6.25 * altura) - (5 * edad)
                tmb = tmb + 5 if genero == "Masculino" else tmb - 161
                
                multiplicadores = {"Sedentario": 1.2, "Ligera": 1.375, "Moderada": 1.55, "Intensa": 1.725}
                calorias_mantenimiento = tmb * multiplicadores[actividad]
                
                if objetivo == "Perder Grasa": calorias_meta = calorias_mantenimiento - 400
                elif objetivo == "Ganar Músculo": calorias_meta = calorias_mantenimiento + 300
                else: calorias_meta = calorias_mantenimiento
                
                # Asignación de macros
                prot = peso * 2.0
                grasa = peso * 0.9
                carbos = (calorias_meta - (prot * 4) - (grasa * 9)) / 4
                
                st.session_state.macros = {
                    "calorias": int(calorias_meta), "proteina": int(prot), 
                    "carbos": int(carbos), "grasas": int(grasa)
                }
                st.success(f"Macros guardados: {int(calorias_meta)} kcal | {int(prot)}g P | {int(carbos)}g C | {int(grasa)}g G")

        # Mostrar macros actuales
        st.subheader("Tus Macros Actuales")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calorías", f"{st.session_state.macros['calorias']} kcal")
        c2.metric("Proteína", f"{st.session_state.macros['proteina']} g")
        c3.metric("Carbohidratos", f"{st.session_state.macros['carbos']} g")
        c4.metric("Grasas", f"{st.session_state.macros['grasas']} g")

    # ---------------------------------------------------------
    # SECCIÓN 2: LISTA DE COMPRAS (GOOGLE FLIGHTS)
    # ---------------------------------------------------------
    elif menu == " Generar Lista de Compras":
        st.header(" Motor de Optimización Multimercado")
        st.write("Calculando tu despensa basándonos en tus macros actuales.")
        
        presupuesto = st.number_input("Presupuesto Semanal (€)", min_value=10.0, value=30.0, step=5.0)
        
        if st.button("Buscar Rutas Más Baratas"):
            opciones, mensaje = algoritmo.generar_opciones_google_flights(st.session_state.macros, presupuesto)
            
            if "Error" in mensaje:
                st.error(mensaje)
            else:
                # CREAMOS LAS PESTAÑAS (TABS)
                nombres_opciones = list(opciones.keys())
                tabs = st.tabs(nombres_opciones)
                
                for i, tab in enumerate(tabs):
                    nombre_opcion = nombres_opciones[i]
                    data = opciones[nombre_opcion]
                    
                    with tab:
                        st.subheader(f"Costo Total: {data['costo']} €")
                        if data['costo'] > presupuesto:
                            st.warning(" Esta opción supera tu presupuesto.")
                        else:
                            st.success(" Dentro del presupuesto.")
                            
                        # Mostrar tabla bonita
                        st.dataframe(data['ticket'], use_container_width=True, hide_index=True)
                        
                        # Añadir esto debajo de st.dataframe(data['ticket']) en app.py
                    with st.expander(" Ver Recetas con estos ingredientes"):
                      recetas = algoritmo.generar_recetas_ia(data['ticket'])
                      st.markdown(recetas)

                    st.button(f"Comprar y Actualizar Alacena ({nombre_opcion})", key=f"btn_comprar_{i}", on_click=algoritmo.guardar_despensa, args=(data['despensa_resultante'],))
                        

    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # SECCIÓN 3: CÁMARA Calc AI (VERSIÓN RASPBERRY PI 5)
    # ---------------------------------------------------------
    elif menu == " Escáner Calc AI (Recalcular)":
        st.header(" Escáner Inteligente de Comidas")
        st.write("¿Comiste fuera del plan? Pon tu plato bajo el escáner y el Coach IA ajustará tu ruta.")
        
        st.sidebar.markdown("---")
        st.sidebar.subheader(" Panel de Demo (Para Jueces)")
        dias_malos = st.sidebar.slider("Simular Días Consecutivos Comiendo Mal", 0, 10, 0)
        
        if st.session_state.user_plan == "Free":
            st.warning(f"Plan Free: Has usado {st.session_state.recalculos_usados} de 3 recálculos esta semana.")
            if st.session_state.recalculos_usados >= 3:
                st.error("Has alcanzado el límite semanal. Ve a 'Upgrade a Premium'.")
                return
        
        # BOTÓN DE HARDWARE PARA LA RASPBERRY PI
        if st.button(" Escanear Plato con Hardware", use_container_width=True):
            st.session_state.recalculos_usados += 1
            
            with st.spinner("Inicializando cámara de la Raspberry Pi 5..."):
                import subprocess
                import os
                
                # Comando nativo de Raspberry Pi 5 para tomar foto.
                # Si lo pruebas en tu laptop de Windows dará error, esto solo funciona dentro de la Raspberry.
                try:
                    subprocess.run(["rpicam-jpeg", "-o", "comida_trampa.jpg", "-t", "1000", "--width", "800", "--height", "600"], check=True)
                    foto_path = "comida_trampa.jpg"
                except Exception as e:
                    # Sistema de rescate si lo estás probando en tu laptop antes de pasarlo a la Raspberry
                    st.warning(" Módulo de cámara Raspberry no detectado (¿Estás en Windows?). Usando imagen de simulación.")
                    foto_path = None # Aquí simularíamos
            
            # Mostramos la foto en Streamlit
            if foto_path and os.path.exists(foto_path):
                st.image(foto_path, caption="Plato detectado por NutriCash Scanner")
            else:
                st.info(" [Imagen simulada de un pedazo de pizza]")
                
            # Llamamos a nuestro mock de la IA
            import camara_ia
            comida_detectada = camara_ia.analizar_imagen_mock(foto_path) # Modificado para aceptar path
            
            st.success(f"**IA Detectó:** {comida_detectada['nombre']} (~{comida_detectada['kcal']} kcal)")
            plan = camara_ia.recalcular_nutricion(comida_detectada['kcal'], dias_malos)
            st.info(f" **Coach NutriCash:** {plan['mensaje_coach']}")
            
            if plan["cambiar_lista_compras"]:
                st.error(" Tu despensa actual ya no cuadra con tus objetivos.")
            else:
                col1, col2 = st.columns(2)
                col1.metric("Ajuste próximas comidas", f"{plan['ajuste_diario']} kcal/día")
                if plan["sugerencia_cardio"]:
                    col2.metric("Actividad Sugerida", "Cardio", delta=plan["sugerencia_cardio"], delta_color="inverse")

    # ---------------------------------------------------------
    # SECCIÓN 4: UPGRADE REDUNIQ
    # ---------------------------------------------------------
    elif menu == " Upgrade a Premium":
        st.header(" Desbloquea NutriCash Premium")
        
        if st.session_state.user_plan == "Premium":
            st.success("¡Ya eres usuario Premium! Disfruta de recálculos ilimitados y la mejor experiencia.")
            st.balloons()
        else:
            st.write("Como usuario Free, estás limitado a 3 recálculos semanales con IA y ves publicidad.")
            st.write("Pásate a Premium para:")
            st.markdown("-  Escáner de comida ILIMITADO.\n-  Zero publicidad.\n-  Integración directa con Prozis y Zumub.")
            
            # Llamamos a nuestra función de REDUNIQ
            pago_exitoso = pagos.simular_pago_reduniq()
            
            if pago_exitoso:
                st.session_state.user_plan = "Premium"
                # Forzamos recarga de la página para que la interfaz se actualice
                time.sleep(2)
                st.rerun()
    # ---------------------------------------------------------
    # SECCIÓN NUEVA: CHATBOT NUTRICIONAL
    # ---------------------------------------------------------
    elif menu == "💬 Habla con tu Coach IA":
        coach_ia.mostrar_chat_nutricionista()
                

# --- CONTROL DE FLUJO ---
if not st.session_state.logged_in:
    mostrar_login()
else:
    mostrar_app_principal()