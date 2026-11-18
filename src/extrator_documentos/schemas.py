from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum

class TipoDocumento(str, Enum):
    NOTA_FISCAL = "nota_fiscal"
    CURRICULO = "curriculo"
    CONTRATO = "contrato"

# --- 1. Schema: Nota Fiscal ---
class ItemNota(BaseModel):
    descricao: str
    quantidade: float = Field(gt=0)
    valor_unitario: float = Field(ge=0)
    valor_total: float = Field(ge=0)

class NotaFiscalSchema(BaseModel):
    numero_nota: str
    cnpj_emissor: str = Field(description="Apenas números, 14 dígitos")
    nome_emissor: str
    data_emissao: str = Field(description="Formato YYYY-MM-DD")
    valor_total: float = Field(gt=0)
    itens: List[ItemNota]

    @field_validator("cnpj_emissor")
    @classmethod
    def validar_cnpj(cls, v: str) -> str:
        apenas_numeros = "".join(filter(str.isdigit, v))
        if len(apenas_numeros) != 14:
            raise ValueError("O CNPJ deve conter exatamente 14 dígitos numéricos.")
        return apenas_numeros

# --- 2. Schema: Currículo ---
class ExperienciaProfissional(BaseModel):
    empresa: str
    cargo: str
    periodo: str
    resumo_atividades: str

class CurriculoSchema(BaseModel):
    nome_completo: str
    email: str
    telefone: Optional[str] = None
    habilidades: List[str]
    experiencias: List[ExperienciaProfissional]

# --- 3. Schema: Contrato ---
class ContratoSchema(BaseModel):
    contratante: str
    contratado: str
    objeto_contrato: str
    valor_mensal_ou_total: float = Field(ge=0)
    prazo_vigencia: str
    foro_eleito: Optional[str] = None