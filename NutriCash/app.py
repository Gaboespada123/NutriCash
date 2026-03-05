import flet as ft
from models import UserProfile
from calculator import calculate_user_macros

def main(page: ft.Page):
    # --- CONFIGURAÇÕES DA JANELA (Novo Padrão Flet 0.80+) ---
    page.title = "NutriCash - Onboarding"
    page.window.width = 400      # Na versão antiga era page.window_width
    page.window.height = 800     # Na versão antiga era page.window_height
    page.window.resizable = False # Na versão antiga era page.window_resizable
    page.theme_mode = "light"
    page.padding = 0
    
    # Paleta de Cores
    VERDE_ESCURO = "#2D6A4F"
    VERDE_CLARO = "#95D5B2"
    BRANCO = "#F8F9FA"

    # --- CAMPOS DO FORMULÁRIO ---
    nome_input = ft.TextField(label="Nome", border_radius=15, prefix_icon="person")
    idade_input = ft.TextField(label="Idade", border_radius=15, keyboard_type="number")
    peso_input = ft.TextField(label="Peso (kg)", border_radius=15, keyboard_type="number")
    altura_input = ft.TextField(label="Altura (cm)", border_radius=15, keyboard_type="number")
    
    genero_dropdown = ft.Dropdown(
        label="Género",
        border_radius=15,
        options=[
            ft.dropdown.Option(key="Masculino", text="Masculino"), 
            ft.dropdown.Option(key="Feminino", text="Feminino")
        ]
    )
    
    objetivo_dropdown = ft.Dropdown(
        label="Objetivo",
        border_radius=15,
        options=[
            ft.dropdown.Option(key="perder_peso", text="Perder Peso"),
            ft.dropdown.Option(key="manter", text="Manter"),
            ft.dropdown.Option(key="ganhar_massa", text="Ganhar Massa")
        ]
    )
    
    atividade_dropdown = ft.Dropdown(
        label="Nível de Atividade",
        border_radius=15,
        options=[
            ft.dropdown.Option(key="sedentario", text="Sedentário"),
            ft.dropdown.Option(key="moderado", text="Moderado"),
            ft.dropdown.Option(key="ativo", text="Ativo")
        ]
    )
    
    orcamento_input = ft.TextField(
        label="Orçamento Semanal (€)", 
        border_radius=15, 
        keyboard_type="number"
    )

    # --- FUNÇÃO DE TRANSIÇÃO (CÁLCULO) ---
    def gerar_plano_click(e):
        try:
            # 1. Criar objeto temporário para cálculo
            user = UserProfile(
                name=nome_input.value,
                age=int(idade_input.value),
                weight=float(peso_input.value),
                height=float(altura_input.value),
                gender=genero_dropdown.value,
                goal=objetivo_dropdown.value,
                activity_level=atividade_dropdown.value,
                weekly_budget=float(orcamento_input.value),
                preferred_supermarket="Lidl",
                target_protein=0, target_carbs=0, target_fats=0, target_calories=0
            )

            # 2. Calcular Macros
            user_calculado = calculate_user_macros(user)

            # 3. Atualizar a UI
            form_container.visible = False
            resumo_container.visible = True
            
            val_cal.value = f"{user_calculado.target_calories} kcal"
            val_prot.value = f"{user_calculado.target_protein}g"
            val_carb.value = f"{user_calculado.target_carbs}g"
            val_fat.value = f"{user_calculado.target_fats}g"
            
            page.update()
            
        except Exception as ex:
            # Novo Padrão Flet 0.80+ para abrir barras de notificação de erro
            erro_snack = ft.SnackBar(ft.Text("Erro: Preencha todos os campos com números válidos!"))
            page.open(erro_snack)

    # --- CONTENTORES DA INTERFACE ---
    val_cal = ft.Text(size=30, weight="bold", color=VERDE_ESCURO)
    val_prot = ft.Text(size=20, weight="bold")
    val_carb = ft.Text(size=20, weight="bold")
    val_fat = ft.Text(size=20, weight="bold")

    resumo_container = ft.Column(
        visible=False,
        horizontal_alignment="center",
        controls=[
            ft.Icon("check_circle", color=VERDE_ESCURO, size=60),
            ft.Text("O teu Plano NutriCash", size=24, weight="bold", color=VERDE_ESCURO),
            ft.Divider(height=20, color="transparent"),
            ft.Container(
                content=ft.Column([
                    ft.Text("Calorias Diárias", color="black54"),
                    val_cal,
                ], horizontal_alignment="center"),
                bgcolor=VERDE_CLARO, padding=20, border_radius=20, width=300
            ),
            ft.Row([
                ft.Container(content=ft.Column([ft.Text("Prot"), val_prot]), bgcolor=BRANCO, padding=15, border_radius=15, expand=True, border=ft.border.all(1, VERDE_CLARO)),
                ft.Container(content=ft.Column([ft.Text("Carb"), val_carb]), bgcolor=BRANCO, padding=15, border_radius=15, expand=True, border=ft.border.all(1, VERDE_CLARO)),
                ft.Container(content=ft.Column([ft.Text("Fat"), val_fat]), bgcolor=BRANCO, padding=15, border_radius=15, expand=True, border=ft.border.all(1, VERDE_CLARO)),
            ], spacing=10),
            ft.ElevatedButton(
                "Entrar na App", 
                color=BRANCO, bgcolor=VERDE_ESCURO, 
                on_click=lambda _: print("Pronto para o Dashboard"),
                width=300, height=50
            )
        ]
    )

    form_container = ft.Column(
        scroll="hidden",
        controls=[
            ft.Text("Bem-vindo ao NutriCash", size=28, weight="bold", color=VERDE_ESCURO),
            ft.Text("Vamos configurar o teu perfil de saúde.", color="black54"),
            ft.Divider(height=20),
            nome_input,
            ft.Row([idade_input, genero_dropdown]),
            ft.Row([peso_input, altura_input]),
            objetivo_dropdown,
            atividade_dropdown,
            orcamento_input,
            ft.ElevatedButton(
                "Gerar Plano",
                bgcolor=VERDE_ESCURO,
                color=BRANCO,
                height=50,
                width=400,
                on_click=gerar_plano_click
            )
        ]
    )

    page.add(
        ft.Container(
            content=ft.Column([form_container, resumo_container]),
            padding=20,
            expand=True,
            bgcolor=BRANCO
        )
    )

# Executar a app (método oficial mais recente)
ft.app(main)