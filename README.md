# WineAI 🍷

Wine AI is a backend service designed to act as an **intelligent pocket sommelier** via **WhatsApp**. The idea is that users chat through the app and get an assistant that can answer questions about wine, recommend bottles, and help choose the right one based on context, preferences, and food pairing.

The project is aimed at **people who are curious about wine** and want an intelligent sommelier always at hand on their phone, with automated and personalized interactions.

The service is built with a focus on **simple, scalable, cloud-native architecture**, running on **Google Cloud Platform (GCP)** using **lightweight Python services**.

---

# Project Goal

Wine AI aims to create a **wine recommendation and knowledge service** capable of:

- answering questions about wines
- recommending bottles
- suggesting food pairings
- assisting customers during purchase decisions
- automating wine-related customer interactions
- integrating with external systems

Potential use cases include:

- wine e-commerce platforms
- physical wine shops
- recommendation kiosks
- chatbots
- mobile apps
- messaging platforms (e.g., WhatsApp)

---

# Architecture

The project follows **Clean Architecture principles**, separating responsibilities into layers to keep the domain logic independent from infrastructure concerns.

## Twilio WhatsApp Integration

The WhatsApp messaging flow uses a provider adapter in `infrastructure/external/twilio_whatsapp_client.py`.
Domain services remain unaware of Twilio and depend only on a messaging gateway contract with a `send_text` callable.

Required environment variables:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`

The webhook endpoint remains available at `/webhook/whatsapp` and expects the standard Twilio WhatsApp webhook payload.
