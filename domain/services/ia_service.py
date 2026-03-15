from logging import info
from infrastructure.external.claude_client import ClaudeClient

class IAService:
    def generate_response(customer, user_message):
        """
        Orquestra a criação do prompt, chama o modelo de linguagem
        e retorna apenas o texto final para o usuário.
        """
        client_context = create_client_context(customer)

        prompt = (
            "Você é um sommelier virtual especializado em vinhos. "
            "Responda sempre em português do Brasil, de forma clara, "
            "amigável e concisa. Se não tiver certeza, seja honesto."
        )

        user_prompt = (
            f"Contexto do cliente:\n{client_context}\n\n"
            f"Mensagem do cliente:\n\"{user_message}\"\n\n"
            "Responda com uma recomendação ou explicação adequada, "
            "podendo sugerir vinhos, harmonizações e faixas de preço."
        )

        info(user_prompt)

        response = ClaudeClient.generate(
            system_prompt=prompt,
            user_prompt=user_prompt,
        )

        return response.strip()

def create_client_context(customer):
    if not customer:
        return "Cliente desconhecido (nenhum dado cadastrado)."

    plano = customer.get("plan", "desconhecido")
    nome = customer.get("name", "Cliente")
    status = customer.get("status", "desconhecido")

    return (
        f"Nome: {nome}\n"
        f"Status: {status}\n"
        f"Plano: {plano}\n"
    )

