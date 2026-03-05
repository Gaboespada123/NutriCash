import os
from dotenv import load_dotenv
from supabase import create_client, Client
from models import UserProfile

# Carrega as variáveis do ficheiro .env
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("As credenciais do Supabase não foram encontradas. Verifica o ficheiro .env.")

# Inicializa a ligação ao Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_user(user_data: UserProfile):
    """Insere um novo perfil de utilizador na tabela 'profiles'."""
    # model_dump() converte o modelo Pydantic num dicionário do Python
    data = user_data.model_dump()
    response = supabase.table("profiles").insert(data).execute()
    return response.data

def get_user(user_id: str):
    """Vai buscar um utilizador específico através do seu ID."""
    response = supabase.table("profiles").select("*").eq("id", user_id).execute()
    return response.data

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from models import UserProfile

# Carrega as variáveis do ficheiro .env
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("As credenciais do Supabase não foram encontradas. Verifica o ficheiro .env.")

# Inicializa a ligação ao Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_user(user_data: UserProfile):
    """Insere um novo perfil de utilizador na tabela 'profiles'."""
    # model_dump() converte o modelo Pydantic num dicionário do Python
    data = user_data.model_dump()
    response = supabase.table("profiles").insert(data).execute()
    return response.data


