import os
import json
from dotenv import load_dotenv

# Importações das nossas 5 Fases
from models import UserProfile
import database
import calculator
import ai_coach
import gps_logic
import scraper

# Carregar variáveis de ambiente (.env)
load_dotenv()

def run_nutricash_simulation():
    print("🚀 A iniciar o Ecossistema NutriCash...\n")

    try:
        # --- PASSO A: Registo (UserProfile) ---
        # Criamos o perfil inicial do João
        joao = UserProfile(
            name="João Nutri",
            age=30,
            weight=85.0,
            height=180.0,
            gender="M",
            goal="perder_peso",
            activity_level="moderado",
            weekly_budget=60.0,
            preferred_supermarket="Continente",
            target_protein=0, target_carbs=0, target_fats=0, target_calories=0 # Inicialmente a zero
        )
        print(f"👤 Passo A: Perfil de {joao.name} criado.")

        # --- PASSO B: Cálculo Inicial ---
        # Definimos os macros alvo originais
        joao = calculator.calculate_user_macros(joao)
        print(f"📊 Passo B: Macros Originais Calculados: {joao.target_calories} kcal/dia.")
        
        # Opcional: Guardar no Supabase (Descomenta se a tua tabela 'profiles' estiver pronta)
        # database.create_user(joao)

        # --- PASSO C & D: O Deslize e Análise IA ---
        confissao = "Ontem à noite não resisti e comi um hambúrguer duplo com batatas fritas e um batido."
        print(f"\n🍔 Passo C: O utilizador confessa: '{confissao}'")
        
        print("🧠 Passo D: A consultar o Coach IA (Gemini)...")
        # Criamos um dict simples para contexto da IA
        macros_atuais = {
            "calorias": joao.target_calories,
            "proteina": joao.target_protein,
            "hidratos": joao.target_carbs,
            "gordura": joao.target_fats
        }
        
        analise_ia = ai_coach.analyze_meal_slip(confissao, macros_atuais)
        
        # --- PASSO E: Recálculo GPS ---
        print("🗺️ Passo E: Recalculando rota para os próximos 3 dias...")
        rota_ajustada = gps_logic.recalculate_route(joao, analise_ia)
        
        # Criamos um perfil temporário com os macros novos para o scraper entender
        novos_macros = rota_ajustada["novos_macros_diarios"]
        joao_ajustado = joao.copy(update={
            "target_calories": novos_macros["calorias"],
            "target_protein": novos_macros["proteina"],
            "target_carbs": novos_macros["hidratos"],
            "target_fats": novos_macros["gordura"]
        })

        # --- PASSO F: Carrinho Inteligente ---
        print("🛒 Passo F: Gerando lista de compras económica para compensação...")
        carrinho = scraper.generate_smart_cart(joao_ajustado)

        # =========================================================
        # RELATÓRIO FINAL (O Momento Uau)
        # =========================================================
        print("\n" + "="*50)
        print("       ✨ RELATÓRIO FINAL NUTRICASH ✨")
        print("="*50)
        
        print(f"\n💌 MENSAGEM DO COACH:")
        print(f"\"{rota_ajustada['mensagem_empatica']}\"")
        
        print(f"\n📈 COMPARAÇÃO DE MACROS (DIÁRIOS):")
        print(f"Original: {joao.target_calories} kcal | P:{joao.target_protein}g | H:{joao.target_carbs}g | G:{joao.target_fats}g")
        print(f"Nova Rota: {novos_macros['calorias']} kcal | P:{novos_macros['proteina']}g | H:{novos_macros['hidratos']}g | G:{novos_macros['gordura']}g")
        
        print(f"\n🛒 LISTA DE COMPRAS SUGERIDA (PRÓXIMOS 3 DIAS):")
        for item in carrinho["carrinho_inteligente"]:
            print(f" - {item['produto']}: {item['quantidade_sugerida_g']}g")
            
        print(f"\n💰 ECONOMIA ESTIMADA: {carrinho['poupanca_estimada_diaria'] * 3:.2f}€ (em 3 dias)")
        print(f"📉 CUSTO TOTAL DIÁRIO: {carrinho['custo_total_diario']:.2f}€")
        print("="*50)

    except Exception as e:
        print(f"\n❌ ERRO NO SISTEMA: {e}")

if __name__ == "__main__":
    run_nutricash_simulation()