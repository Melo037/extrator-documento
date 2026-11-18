from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from extrator_documentos.schemas import TipoDocumento
from extrator_documentos.extractor import extrair_texto_pdf, extrair_com_retentativa
app = FastAPI(
    title="Extrator de Documentos Estruturados",
    description="API para extração validada de PDFs com LLM, Pydantic e Retentativa",
    version="1.0.0",
)

@app.post("/api/v1/extrair")
async def processar_documento(
    tipo_documento: TipoDocumento = Form(..., description="nota_fiscal, curriculo ou contrato"),
    arquivo: UploadFile = File(..., description="Arquivo PDF para extração"),
):
    if arquivo.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="O arquivo enviado deve ser um PDF.")

    try:
        conteudo_bytes = await arquivo.read()
        texto = extrair_texto_pdf(conteudo_bytes)
        resultado = extrair_com_retentativa(texto, tipo_documento, max_tentativas=3)
        return resultado

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=502, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")