import fitz
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from extrator_documentos.main import app

client = TestClient(app)

def criar_pdf_teste(texto: str) -> bytes:
    doc = fitz.open()
    pagina = doc.new_page()
    pagina.insert_text((50, 50), texto)
    return doc.tobytes()

@patch("extrator_documentos.extractor.client.chat.completions.create")
def test_retentativa_automatica_com_sucesso(mock_openai):
    # 1ª resposta simulada da LLM: Inválida (CNPJ com apenas 5 dígitos)
    resposta_invalida = MagicMock()
    resposta_invalida.choices[0].message.content = """
    {
        "numero_nota": "NF-998",
        "cnpj_emissor": "12345",
        "nome_emissor": "Tech Brasil LTDA",
        "data_emissao": "2026-10-15",
        "valor_total": 1500.00,
        "itens": [{"descricao": "Servidor Cloud", "quantidade": 1, "valor_unitario": 1500.0, "valor_total": 1500.0}]
    }
    """

    # 2ª resposta simulada da LLM: Corrigida após o feedback de erro do Pydantic
    resposta_valida = MagicMock()
    resposta_valida.choices[0].message.content = """
    {
        "numero_nota": "NF-998",
        "cnpj_emissor": "12.345.678/0001-99",
        "nome_emissor": "Tech Brasil LTDA",
        "data_emissao": "2026-10-15",
        "valor_total": 1500.00,
        "itens": [{"descricao": "Servidor Cloud", "quantidade": 1, "valor_unitario": 1500.0, "valor_total": 1500.0}]
    }
    """

    mock_openai.side_effect = [resposta_invalida, resposta_valida]

    pdf_bytes = criar_pdf_teste("Nota Fiscal NF-998 - CNPJ 12.345.678/0001-99 - Valor R$ 1500,00")

    response = client.post(
        "/api/v1/extrair",
        data={"tipo_documento": "nota_fiscal"},
        files={"arquivo": ("nota.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    dados = response.json()
    assert dados["sucesso"] is True
    assert dados["tentativas_utilizadas"] == 2
    assert dados["dados"]["cnpj_emissor"] == "12345678000199"