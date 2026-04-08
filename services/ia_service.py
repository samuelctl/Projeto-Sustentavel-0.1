from dotenv import load_dotenv
from google import genai
from fastapi import HTTPException
import json
import os

load_dotenv()


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY não encontrada no ambiente"
        )

    return genai.Client(api_key=api_key)


def gerar_recomendacao_ia(insights: dict):
    client = get_gemini_client()

    prompt = f"""
Você é um assistente financeiro inteligente.

Analise os dados abaixo e gere resposta em JSON puro.
Não use markdown.
Não invente dados.

Dados:
{json.dumps(insights, ensure_ascii=False)}

Formato obrigatório:
{{
  "diagnostico_geral": "texto",
  "alerta_amostra_regional": "texto",
  "nivel_urgencia": "baixo ou medio ou alto",
  "economia_estimativa_mensal": 0,
  "recomendacoes": [
    {{
      "titulo": "texto curto",
      "descricao": "texto prático",
      "categoria": "transporte, alimentacao, agua, energia, produtos ou outros",
      "impacto": "baixo ou medio ou alto"
    }}
  ]
}}

Regras:
- Responder em português
- Máximo 3 recomendações
- Se a amostra regional for pequena, avisar claramente
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        texto = response.text.strip()
        return json.loads(texto)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="A IA respondeu em formato inválido"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na IA: {str(e)}"
        )


def montar_prompt_chat(insights: dict, pergunta: str):
    return f"""
Você é um assistente financeiro inteligente dentro de um aplicativo.

Responda em português do Brasil, de forma clara, objetiva e prática.
Use apenas os dados abaixo.
Não invente números.
Se a amostra regional for pequena, deixe isso claro na resposta.

Dados do usuário:
{json.dumps(insights, ensure_ascii=False)}

Pergunta do usuário:
{pergunta}

Regras:
- Responda como um assistente do app
- Não use markdown
- Seja direto
- Se a amostra regional for pequena, diga isso claramente
"""


def gerar_resposta_chat_ia(insights: dict, pergunta: str):
    client = get_gemini_client()
    prompt = montar_prompt_chat(insights, pergunta)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao conversar com a IA: {str(e)}"
        )