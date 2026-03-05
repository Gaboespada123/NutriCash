from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    name: str = Field(..., description="Nome do utilizador")
    age: int = Field(..., gt=0, description="Idade em anos")
    weight: float = Field(..., gt=0.0, description="Peso em kg")
    height: float = Field(..., gt=0.0, description="Altura em cm")
    gender: str = Field(..., description="Género do utilizador")
    goal: str = Field(..., description="Ex: Perder peso, Manter, Ganhar massa")
    activity_level: str = Field(..., description="Ex: Sedentário, Leve, Moderado, Intenso")
    weekly_budget: float = Field(..., ge=0.0, description="Orçamento semanal em euros")
    preferred_supermarket: str = Field(..., description="Ex: Continente, Pingo Doce, Lidl")
    
    # 4 Macros Alvo
    target_protein: float = Field(..., ge=0.0, description="Proteína em gramas")
    target_carbs: float = Field(..., ge=0.0, description="Hidratos em gramas")
    target_fats: float = Field(..., ge=0.0, description="Gorduras em gramas")
    target_calories: float = Field(..., ge=0.0, description="Calorias totais")