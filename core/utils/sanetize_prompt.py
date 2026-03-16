import re

def sanitize_input(text, max_length=500):
    """Remove padrões de prompt injection e limita o tamanho."""
    if not isinstance(text, str):
        raise ValueError("Entrada inválida.")

    text = text[:max_length]

    patterns = [
        r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions?",
        r"disregard\s+(all\s+)?instructions?",
        r"you\s+are\s+now\s+",
        r"new\s+instructions?:",
        r"system\s*:",
        r"<\s*system\s*>",
        r"\[INST\]",
        r"###\s*instruction",
        r"forget\s+(everything|all)",
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Mensagem não permitida.")

    return text.strip()

def validate_output(text):
    forbidden = ["ignore", "instrução anterior", "novo sistema", "DAN", "jailbreak"]
    for word in forbidden:
        if word.lower() in text.lower():
            return "Desculpe, não consegui gerar uma recomendação agora. Tente novamente!"
    if len(text) > 2000:  # muito longo para WhatsApp
        text = text[:2000] + "..."
    return text