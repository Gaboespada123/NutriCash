import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega as variáveis de ambiente
load_dotenv()

# Vai buscar a chave do Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave GEMINI_API_KEY não foi encontrada no ficheiro .env.")

# Inicializa o NOVO cliente da Google
client = genai.Client(api_key=api_key)

# Definimos as regras de ouro (System Instruction)
system_prompt = (
    'És o Coach NutriCash, um assistente empático em Portugal. NUNCA julgas. '
    'Se o utilizador comer algo fora do plano, ages com empatia e dizes que está tudo bem. '
    'Tens de devolver a resposta OBRIGATORIAMENTE em formato JSON com esta exata estrutura: '
    '{"mensagem_empatica": "A tua resposta amigável", "calorias_a_ajustar": numero, '
    '"hidratos_a_ajustar": numero, "gordura_a_ajustar": numero}. '
    'Os valores numéricos de ajuste devem ser positivos (o que o utilizador excedeu).'
)

def analyze_meal_slip(user_message: str, current_macros: dict) -> dict:
    """
    Analisa um deslize alimentar do utilizador usando a API Gratuita do Gemini (novo SDK).
    """
    user_prompt = f"Macros atuais do plano: {current_macros}\nDeslize do utilizador: {user_message}"

    try:
        # Nova forma de chamar a API com a biblioteca google-genai
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.7
            )
        )
        
        # O Gemini já devolve o texto no formato JSON que pedimos, basta converter
        parsed_data = json.loads(response.text)
        return parsed_data
        
    except Exception as e:
        print(f"❌ Erro ao contactar o Gemini: {e}")
        return {
            "mensagem_empatica": "Parece que a minha ligação falhou um pouco, mas não te preocupes com o que comeste! Amanhã voltamos ao plano com calma.",
            "calorias_a_ajustar": 0,
            "hidratos_a_ajustar": 0,
            "gordura_a_ajustar": 0
        }

