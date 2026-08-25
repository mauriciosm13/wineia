# Agent Guide

## Project Overview

This project is a **Python 3 backend running on Google Cloud Platform (GCP)**.

It follows a **layered architecture inspired by Clean Architecture**, separating HTTP concerns, business logic, and infrastructure.

The system is designed to support:

* WhatsApp messaging flows
* Customer management
* AI wine recommendations
* Scheduled campaigns
* Queue-based message delivery

---

# Architecture

The project is organized into the following main folders:

```
api/
core/
domain/
infrastructure/
```

Each layer has a clear responsibility.

## api

Handles **HTTP interaction**.

Responsibilities:

* routing
* request parsing
* response formatting
* status codes

This layer **must not contain business logic**.

Typical structure:

```
api/
  routes.py
  handlers/
```

Handlers call services from the `domain` layer.

---

## core

Contains **shared infrastructure and configuration**.

Examples:

```
core/
  config.py
  logging.py
  queues.py
```

Responsibilities:

* environment configuration
* logging setup
* queue definitions
* shared utilities

The `core` layer must remain **framework-independent**.

---

## domain

Contains the **business logic of the application**.

This is the most important layer.

Typical structure:

```
domain/
  models/
  services/
  repositories/
  exceptions/
```

Responsibilities:

* business rules
* domain models
* domain services
* repository interfaces

The `domain` layer **must not depend on infrastructure**.

Example rule:

```
domain → cannot import infrastructure
```

---

## infrastructure

Contains **external integrations and implementations**.

Examples:

```
infrastructure/
  datastore/
  repositories/
  external/
  queues/
```

Responsibilities:

* database access
* external APIs
* queue integrations
* cloud services

Examples:

* Google Datastore
* Cloud Tasks
* WhatsApp API
* Claude (Anthropic)

---

# Dependency Rules

Dependencies must follow this direction:

```
api
  ↓
domain
  ↓
infrastructure
```

Rules:

* `domain` must never import `infrastructure`
* `api` must not contain business logic
* external services must live in `infrastructure`

---

# Coding Style

The project follows **PEP8** strictly.

General rules:

* use descriptive variable names
* prefer explicit code over clever code
* keep functions small and focused
* avoid global mutable state

---

# Avoid Using `self`

The project avoids instance-based classes where possible.

Prefer:

* functions
* stateless services
* dependency injection

Example (preferred):

```python
def create_customer(repository, phone, name):
    ...
```

Instead of:

```python
class CustomerService:
    def __init__(self, repository):
        self.repository = repository
```

The codebase favors **stateless design**.

---

# Google Cloud Integration

The system runs on GCP and integrates with:

* Cloud Run
* Cloud Tasks
* Cloud Scheduler
* Datastore (Firestore in Datastore mode)

Infrastructure code should isolate all GCP dependencies.

Example location:

```
infrastructure/datastore/
infrastructure/queues/
```

---

# Queues

Message sending must be **queue-based**.

Architecture:

```
Scheduler
   ↓
Job Endpoint
   ↓
Cloud Tasks Queue
   ↓
Worker Endpoint
   ↓
External API (WhatsApp)
```

Queue definitions should live in:

```
core/queues.py
```

---

# AI Integration

AI integrations (Claude, OpenAI, etc.) must be placed in:

```
infrastructure/external/
```

The `domain` layer should interact through **services**, never directly with the AI client.

---

# API Design

Endpoints should remain minimal.

Example:

```
POST /customers
POST /webhook/whatsapp
POST /jobs/daily-recommendations
POST /workers/send-message
GET  /health
```

Handlers must delegate logic to `domain/services`.

---

# Testing Strategy

Domain logic must be easily testable.

Recommended approach:

* mock repositories
* test domain services independently
* avoid testing infrastructure in unit tests

---

# Future Features

Planned capabilities include:

* wine recommendation engine
* preference learning
* campaign system
* analytics
* AI-assisted recommendations

These features should be implemented within the existing architecture boundaries.

---

# Summary

This repository follows a **clean separation between API, domain, and infrastructure**.

Key principles:

* stateless services
* minimal framework coupling
* strict layer separation
* PEP8 compliance
* cloud-native architecture
