import streamlit as st
from models import UserProfile
from calculator import calculate_user_macros
from ai_coach import analyze_meal_slip
from gps_logic import recalculate_route
from scraper import generate_smart_cart

# 1. Configuração da página
st.set_page_config(page_title="NutriCash", page_icon="🍏", layout="centered")

# 2. Gestão de Estado (Memória da App)
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o teu Coach NutriCash. Comeste algo fora do plano? Confessa aqui, eu não julgo!"}
    ]

def show_onboarding():
    st.title("🍏 Bem-vindo ao NutriCash")
    st.write("Vamos configurar o teu perfil de saúde.")

    # Formulário Streamlit
    with st.form("onboarding_form"):
        nome = st.text_input("Nome")
        
        col1, col2 = st.columns(2)
        idade = col1.number_input("Idade", min_value=10, max_value=120, step=1, value=30)
        genero = col2.selectbox("Género", ["Masculino", "Feminino"])

        col3, col4 = st.columns(2)
        peso = col3.number_input("Peso (kg)", min_value=30.0, max_value=250.0, step=0.1, value=80.0)
        altura = col4.number_input("Altura (cm)", min_value=100.0, max_value=250.0, step=1.0, value=175.0)

        objetivo = st.selectbox("Objetivo", ["Perder Peso", "Manter", "Ganhar Massa"])
        atividade = st.selectbox("Nível de Atividade", ["Sedentário", "Moderado", "Ativo"])
        orcamento = st.number_input("Orçamento Semanal (€)", min_value=10.0, max_value=500.0, step=1.0, value=50.0)

        # Mapeamento para o backend
        obj_map = {"Perder Peso": "perder_peso", "Manter": "manter", "Ganhar Massa": "ganhar_massa"}
        act_map = {"Sedentário": "sedentario", "Moderado": "moderado", "Ativo": "ativo"}

        submitted = st.form_submit_button("Entrar na App", use_container_width=True)

        if submitted:
            if nome.strip() == "":
                st.error("Por favor, preenche o teu nome para avançar!")
            else:
                user = UserProfile(
                    name=nome,
                    age=int(idade),
                    weight=float(peso),
                    height=float(altura),
                    gender="M" if genero == "Masculino" else "F",
                    goal=obj_map[objetivo],
                    activity_level=act_map[atividade],
                    weekly_budget=float(orcamento),
                    preferred_supermarket="Continente",
                    target_protein=0, target_carbs=0, target_fats=0, target_calories=0
                )
                
                # Executa a matemática e guarda na memória
                st.session_state.user_data = calculate_user_macros(user)
                st.rerun()

def show_dashboard():

    user = st.session_state.user_data

    # Header
    st.success(f"Olá, **{user.name}**! 🟢 GPS Ativo")
    st.subheader("O teu Painel de Instrumentos")


    # Grelha de Macros (Agora 100% Dinâmica e Viva!)
    col1, col2, col3, col4 = st.columns(4)

    # Função segura para ir buscar o que já foi consumido (se o teu backend usar 'consumed_calories' ou 'current_calories')
    # Se o teu backend apenas subtrair aos targets, o valor consumido ficará a 0 mas o target descerá.
    cons_cal = getattr(user, 'consumed_calories', getattr(user, 'current_calories', 0))
    cons_prot = getattr(user, 'consumed_protein', getattr(user, 'current_protein', 0))
    cons_carb = getattr(user, 'consumed_carbs', getattr(user, 'current_carbs', 0))
    cons_fat = getattr(user, 'consumed_fats', getattr(user, 'current_fats', 0))

    # Prevenção de divisão por zero para as barras de progresso
    prog_cal = min(cons_cal / user.target_calories if user.target_calories > 0 else 0.0, 1.0)
    prog_prot = min(cons_prot / user.target_protein if user.target_protein > 0 else 0.0, 1.0)
    prog_carb = min(cons_carb / user.target_carbs if user.target_carbs > 0 else 0.0, 1.0)
    prog_fat = min(cons_fat / user.target_fats if user.target_fats > 0 else 0.0, 1.0)

    with col1:
        st.metric(label="🔥 Calorias", value=f"{int(cons_cal)} / {int(user.target_calories)}", delta="kcal", delta_color="off")
        st.progress(prog_cal)

    with col2:
        st.metric(label="🥩 Proteína", value=f"{int(cons_prot)} / {int(user.target_protein)}", delta="g", delta_color="off")
        st.progress(prog_prot)

    with col3:
        st.metric(label="🌾 Hidratos", value=f"{int(cons_carb)} / {int(user.target_carbs)}", delta="g", delta_color="off")
        st.progress(prog_carb)

    with col4:
        st.metric(label="💧 Gordura", value=f"{int(cons_fat)} / {int(user.target_fats)}", delta="g", delta_color="off")
        st.progress(prog_fat)


    # --- COLAR NO FINAL DA FUNÇÃO show_dashboard() ---
    st.divider()
    st.subheader("💬 Coach NutriCash")

    # Desenhar todo o histórico de mensagens guardado na memória
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    # --- COLAR LOGO A SEGUIR AO BLOCO 2 ---
    prompt = st.chat_input("Ex: Comi uma fatia de bolo de chocolate...")

    if prompt:
        # 1. Guardar e desenhar o que o utilizador escreveu
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # 2. A Magia acontece aqui dentro do Spinner
        with st.spinner("A analisar o impacto e a recalcular a rota..."):
            try:
                # Chama a IA para ler a refeição
                slip_data = analyze_meal_slip(prompt, st.session_state.user_data)
                
                # Recalcula o GPS Nutricional
                nova_rota = recalculate_route(st.session_state.user_data, slip_data)
                
                # --- O MAPEMENTO MÁGICO (O Tradutor) ---
                if "novos_macros_diarios" in nova_rota:
                    novos_dados = nova_rota["novos_macros_diarios"]
                    
                    # Atualizamos o nosso Perfil exatamente com as gavetas que a interface usa
                    st.session_state.user_data.target_calories = novos_dados.get("calorias", st.session_state.user_data.target_calories)
                    st.session_state.user_data.target_protein = novos_dados.get("proteina", st.session_state.user_data.target_protein)
                    st.session_state.user_data.target_carbs = novos_dados.get("hidratos", st.session_state.user_data.target_carbs)
                    st.session_state.user_data.target_fats = novos_dados.get("gordura", st.session_state.user_data.target_fats)
                # ----------------------------------------
                
                # Resposta Empática
                resposta = nova_rota.get("mensagem_empatica", "Rota recalculada! Vamos focar-nos no resto do dia.")
                st.session_state.messages.append({"role": "assistant", "content": resposta})
                
                # Força a página a recarregar de imediato
                st.rerun()
                
            except Exception as e:
                st.error(f"Ups, falha na comunicação com o satélite: {e}")

    st.divider()
    st.header("🛒 Carrinho Inteligente NutriCash")
    st.write("Vamos transformar os teus macros de hoje numa lista de compras focada em poupança.")

    # O botão chamativo (Bloco 2) e a Lógica Mágica (Bloco 3)
    if st.button("Gerar Lista de Compras Otimizada", type="primary"):
        with st.spinner("A analisar preços no supermercado e a procurar promoções..."):
            try:
                # 1. Chama a função do teu scraper enviando o perfil do utilizador
                cart_data = generate_smart_cart(st.session_state.user_data)
                
                # 2. Desenha as métricas de impacto financeiro
                st.subheader("O teu Talão de Poupança")
                col_preco, col_poupanca = st.columns(2)
                
                with col_preco:
                    st.metric(
                        label="Custo Total Estimado", 
                        value=f"€{cart_data['total_cost']:.2f}"
                    )
                
                with col_poupanca:
                    st.metric(
                        label="Poupança NutriCash", 
                        value=f"€{cart_data['savings']:.2f}", 
                        delta="Abaixo da média nacional!", # Dá aquele toque verde visual do Streamlit
                        delta_color="normal" 
                    )
                
                # 3. Desenha a tabela de compras de forma moderna
                st.write("**A tua Lista de Supermercado:**")
                st.dataframe(
                    cart_data['cart_items'], 
                    use_container_width=True, # Faz a tabela ocupar a largura toda
                    hide_index=True # Remove aquela coluna de números (0, 1, 2...) para ficar mais limpo
                )
                
                st.success("Lista gerada com sucesso! Podes tirar print e ir às compras. 🏃‍♂️💨")
                
            except Exception as e:
                st.error(f"Erro ao ligar ao satélite dos supermercados: {e}")
    # --- FIM DO BLOCO DO CARRINHO ---

    if st.button("Voltar ao Formulário"):
        st.session_state.user_data = None
        st.rerun()

# 3. Roteamento (Routing)
if st.session_state.user_data is None:
    show_onboarding()
else:
    show_dashboard()