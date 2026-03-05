import streamlit as st
import time

def simular_pago_reduniq():
    """
    Simula la pasarela de pago de REDUNIQ para el upgrade a Premium.
    Retorna True si el pago es "exitoso".
    """
    st.markdown("---")
    st.markdown("### 🔒 Checkout Seguro con REDUNIQ")
    st.info("Estás a punto de adquirir **NutriCash Premium** por 4.99€/mes.")
    
    with st.form("reduniq_form"):
        st.text_input("Nombre en la tarjeta", placeholder="João Silva")
        st.text_input("Número de Tarjeta", placeholder="XXXX XXXX XXXX XXXX", max_chars=19)
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Fecha de Expiración", placeholder="MM/AA", max_chars=5)
        with col2:
            st.text_input("CVV", type="password", max_chars=3)
        
        submit = st.form_submit_button("💳 Confirmar Pago de 4.99€")
        
    if submit:
        with st.spinner("Procesando transacción en entorno seguro REDUNIQ..."):
            time.sleep(2.5) # Simula el tiempo que tarda el banco en responder
        st.success("✅ Transacción aprobada. ¡Bienvenido a NutriCash Premium!")
        st.balloons()
        return True
    
    return False