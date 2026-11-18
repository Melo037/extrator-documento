# Extrator de Documentos com Saída Estruturada

API em Python para extrair dados estruturados (JSON) de arquivos PDF — como **notas fiscais**, **currículos** e **contratos** — utilizando LLM com validação estrita via **Pydantic**, loop automático de retentativa e integração pronta para **n8n**.

## O que o projeto faz

- **Extração de texto:** lê PDFs enviados via `multipart/form-data` utilizando `PyMuPDF`.
- **Controle de saída da LLM:** força o retorno em JSON seguindo rigorosamente o schema do tipo de documento escolhido (`nota_fiscal`, `curriculo` ou `contrato`).
- **Validação e autocorreção:** valida a resposta com Pydantic (incluindo regras de negócio como formato de CNPJ e valores positivos). Caso a LLM retorne dados inválidos, o erro de validação é devolvido ao modelo para correção automática (até 3 tentativas).
- **Automação com n8n:** inclui workflow exportável (`n8n_workflow.json`) para receber PDFs via Webhook, acionar a API e devolver o JSON validado.

## Stack

- **Python** + **uv** (gerenciamento de dependências e ambiente)
- **FastAPI** + **Uvicorn**
- **Pydantic v2**
- **PyMuPDF**
- **Google Gemini** (via SDK compatível com OpenAI)
- **Pytest** + **HTTPX** (testes automatizados com mock)
- **n8n**

## Como rodar localmente

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/extrator-documentos.git](https://github.com/SEU-USUARIO/extrator-documentos.git)
   cd extrator-documentos
