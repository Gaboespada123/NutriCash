import streamlit as st
import google.generativeai as genai

# Recuerda configurar tu API Key en app.py o aquí
genai.configure(api_key="AIzaSyD6Je2Ye6V5quJWZYq9SrdhU_G3IR-uCMY")

def mostrar_chat_nutricionista():
    st.header("💬 Tu Coach Nutricional IA")
    st.write("Pregúntame sobre tus macros, cómo sustituir ingredientes o pide consejos para ahorrar en el supermercado.")

    # 1. Inicializar la memoria visual del chat en Streamlit
    if "mensajes_chat" not in st.session_state:
        st.session_state.mensajes_chat = [
            {"role": "assistant", "content": "¡Hola! Soy tu Coach NutriCash 🍏. ¿En qué te puedo ayudar hoy con tu dieta o tu presupuesto?"}
        ]

    # 2. Inicializar el motor de Gemini con "memoria" nativa
    if "chat_gemini" not in st.session_state:
        try:
            # Usamos el modelo Flash que es ultra rápido para chats
            modelo = genai.GenerativeModel('gemini-1.5-flash')
            # start_chat() crea una sesión que recuerda automáticamente el historial
            st.session_state.chat_gemini = modelo.start_chat(history=[])
        except Exception as e:
            st.error("⚠️ Configura tu API Key de Gemini para activar el chat.")
            return

    # 3. Dibujar todos los mensajes pasados en la pantalla
    for mensaje in st.session_state.mensajes_chat:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])

    # 4. La barra inferior donde el usuario escribe
    prompt_usuario = st.chat_input("Escribe tu duda aquí (ej. ¿Qué ceno si me quedé sin calorías?)...")

    if prompt_usuario:
        # A. Guardar y mostrar lo que escribió el usuario
        st.session_state.mensajes_chat.append({"role": "user", "content": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        # B. Consultar a Gemini inyectándole su "Personalidad"
        with st.chat_message("assistant"):
            with st.spinner("Escribiendo..."):
                try:
                    # Le inyectamos las reglas de negocio en silencio antes de su pregunta
                    instruccion_sistema = f"""
                    Instrucción secreta: Eres el Coach IA de la app NutriCash. Eres un nutricionista experto y asesor financiero de supermercados en Portugal. 
                    Responde de forma empática, profesional, motivadora y MUY breve (máximo 2 párrafos).
                    Pregunta del usuario: {prompt_usuario}
                    """
                    
                    # Enviamos el mensaje al chat con memoria
                    respuesta = st.session_state.chat_gemini.send_message(instruccion_sistema)
                    texto_respuesta = respuesta.text
                    
                    # Mostrar y guardar la respuesta de la IA
                    st.markdown(texto_respuesta)
                    st.session_state.mensajes_chat.append({"role": "assistant", "content": texto_respuesta})
                    
                except Exception as e:
                    st.error(f"Hubo un problema de conexión con el cerebro IA: {e}")