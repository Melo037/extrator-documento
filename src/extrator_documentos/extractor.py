import os
import json
import pymupdf as fitz
from typing import Type
from pydantic import BaseModel, ValidationError
from openai import OpenAI
from extrator_documentos.schemas import (
    TipoDocumento,
    NotaFiscalSchema,
    CurriculoSchema,
    ContratoSchema,
)

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

MAPA_SCHEMAS: dict[TipoDocumento, Type[BaseModel]] = {
    TipoDocumento.NOTA_FISCAL: NotaFiscalSchema,
    TipoDocumento.CURRICULO: CurriculoSchema,
    TipoDocumento.CONTRATO: ContratoSchema,
}

def extrair_texto_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    texto = ""
    for pagina in doc:
        texto += pagina.get_text("text") + "\n"
    if not texto.strip():
        raise ValueError("O PDF está vazio ou contém apenas imagens sem OCR.")
    return texto

def extrair_com_retentativa(
    texto_documento: str,
    tipo_doc: TipoDocumento,
    max_tentativas: int = 3
) -> dict:
    schema_model = MAPA_SCHEMAS[tipo_doc]
    json_schema = json.dumps(schema_model.model_json_schema(), ensure_ascii=False, indent=2)

    mensagens = [
        {
            "role": "system",
            "content": (
                "Você é um extrator de dados de alta precisão. "
                "Extraia as informações do documento e retorne APENAS um objeto JSON válido "
                f"que respeite estritamente este JSON Schema:\n{json_schema}"
            ),
        },
        {
            "role": "user",
            "content": f"Extraia os dados do seguinte documento ({tipo_doc.value}):\n\n{texto_documento}",
        },
    ]

    ultimo_erro = ""

    for tentativa in range(1, max_tentativas + 1):
        try:
            resposta = client.chat.completions.create(
                model="gemini-4-hydrogen",
                response_format={"type": "json_object"},
                messages=mensagens,
                temperature=0.0,
            )
            conteudo_json = resposta.choices[0].message.content

            # Valida o JSON contra as regras do Pydantic
            dados_validados = schema_model.model_validate_json(conteudo_json)

            return {
                "sucesso": True,
                "tentativas_utilizadas": tentativa,
                "tipo_documento": tipo_doc.value,
                "dados": dados_validados.model_dump(),
            }

        except (ValidationError, json.JSONDecodeError) as erro:
            ultimo_erro = str(erro)
            # Alimenta a conversa com o erro de validação para a LLM se autocorrigir
            mensagens.append({"role": "assistant", "content": conteudo_json or "{}"})
            mensagens.append(
                {
                    "role": "user",
                    "content": (
                        f"A sua resposta falhou na validação Pydantic com o seguinte erro:\n{ultimo_erro}\n\n"
                        "Corrija os campos inválidos e retorne apenas o JSON corrigido."
                    ),
                }
            )

    raise RuntimeError(
        f"Falha ao validar saída após {max_tentativas} tentativas. Último erro: {ultimo_erro}"
    )