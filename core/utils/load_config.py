def load_config():
    import os

    return {
        "ANTHROPIC_API_MODEL": os.environ["ANTHROPIC_API_MODEL"],
        "ANTHROPIC_API_KEY": os.environ["ANTHROPIC_API_KEY"],
        "account_sid": os.environ["TWILIO_ACCOUNT_SID"],
        "auth_token": os.environ["TWILIO_AUTH_TOKEN"],
        "numberTwillio": os.environ["TWILIO_WHATSAPP_FROM"],
    }
        
