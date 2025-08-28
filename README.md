# 2FA-Middleware

![Project Logo](doc/images/2fa-logo.png)

2FA-Middleware is a secure authentication middleware for FastAPI applications, integrating Keycloak for user authentication and 2-factor authentication (2FA) via email, Time-based One-Time Password (TOTP), and SMS. It provides a robust and flexible authentication solution for frontend applications. In this project a simple React frontend application will be used to demonistrate this concept.

## Key features:

- Keycloak Integration: Seamlessly integration Keycloak for user management and authentication, leveraging its robust identity and integrate external identity providers.
- 2-Factor Authentication: Implement 2FA using various methods, including email, TOTP (e.g., Google Authenticator), and SMS, ensuring an additional layer of security for your application.
- OTP SMS and Email confirmations.

## Architecture

- Keycloak handles authentication and issues JWT tokens.

- FastAPI acts as the central orchestrator, validating tokens and routing requests.

- PostgreSQL stores persistent data like user profiles, transactions, etc.

- Redis manages session data for quick access and scalability.

- SMTP is used by FastAPI to send emails.

- SMS API is triggered by FastAPI to send messages.

![2FA Middleware Architecture](doc/images/2FA-MIDDLEWARE_ARCH.svg)

## RDBMS Schema

RDBMS schema consists of a single table, user_profile.

![ER Diagram](doc/images/ER-DIAGRAM.svg)

## 📋 Run environemnt prerequisites

- 🐍 Python 3.13
- ⚡ Redis
- 🐘 PostgreSQL
- 🌐 Internet connection
- 📧 Email account
- ✍️ API Key for sending SMS
- 📱 Mobile Phone with Google Authenticator

## Recommended Run Environment

(Based on preequirests all requirements covered in DockerCompose file)

- 🦭 Podman/ 🐋 Docker
- 🌐 Internet connection
- 📧 Email account
- ✍️ API Key for sending SMS
- 📱 Mobile Phone with Google Authenticator

## Impelemntation Info

### ⚙️ FastAPI Routes

| HTTP Method | Endpoint          | Description                                 | Who Can Access?             |
| ----------- | ----------------- | ------------------------------------------- | --------------------------- |
| GET         | /metrics          | Returned prometheus_client metrics          | Public                      |
| POST        | /user             | Register first time logged in Keyclock user | Authenticated Keyclock user |
| GET         | /user             | Get current user details                    | Authenticated Keyclock user |
| UPDATE      | /user             | Manual update for user mobile/email         | Authenticated Keyclock user |
| POST        | /user/verify-otp  | Verify received OTP                         | Authenticated Keyclock user |
| POST        | /user/verift-totp | Vertify access for session                  | Authenticated Keyclock user |

## 📦 Libraries Used

### 🐍 Python Backend Application

| Tool/Library          | Purpose                                                               |
| --------------------- | --------------------------------------------------------------------- |
| **FastAPI**           | High-performance web framework for building APIs with Python          |
| **Uvicorn**           | ASGI server used to run FastAPI applications                          |
| **Pydantic**          | Data validation and settings management using Python type annotations |
| **Httpx**             | Asynchronous HTTP client for making API requests                      |
| **Pytop**             | Real-time system monitoring tool for Python applications              |
| **SQLAlchemy**        | SQL toolkit and ORM for database interaction                          |
| **Asyncpg**           | Fast PostgreSQL database driver for asyncio-based applications        |
| **QRCode**            | Library for generating QR codes in Python                             |
| **Redis**             | Data store used for caching, pub/sub, and session management          |
| **prometheus_client** | Export metrics for Prometheus monitoring                              |

### 🧪 Testing CI/CD

| Tool/Library  | Purpose                                                           |
| ------------- | ----------------------------------------------------------------- |
| **Pytest**    | Framework for writing and running unit tests                      |
| **httpx**     | Used for testing HTTP endpoints with async support                |
| **fakeredis** | Simulates Redis for testing without requiring a live Redis server |
