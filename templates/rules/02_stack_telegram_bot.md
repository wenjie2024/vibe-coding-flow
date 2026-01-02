---
description: Telegram Bot & Mini App Development Best Practices
globs: *.py, *.js, *.ts, *.html
---

# Rule 02: Telegram Bot & Mini App Best Practices

## Core Principles
- **Privacy First**: Only collect minimal required data.
- **Webhook over Polling**: Always prefer Webhooks for production bots.
- **Async First**: Use asynchronous libraries (e.g., `aiogram`, `python-telegram-bot` async mode).

## Bot Development (Python)
- **Framework**: Use `python-telegram-bot` (v20+) or `aiogram` (v3+).
- **Error Handling**: Wrap handlers in try-except blocks; log errors; do NOT crash the bot loop.
- **Rate Limiting**: Respect Telegram API limits (30 msgs/sec max). Use queues if necessary.
- **Security**: strict validation of `initData` hash on server-side.

## Mini Apps (Web Apps)
- **UI/UX**: Use `Telegram.WebApp` methods for native feel (`MainButton`, `BackButton`, `HapticFeedback`).
- **Theme**: Listen to `themeChanged` event to adapt to user's Telegram theme (dark/light).
- **Validation**: MUST validate `initData` on backend before trusting user identity.
- **Navigation**: Handle hardware back button (Android) via `BackButton.onClick`.

## Deployment
- **HTTPS**: Required for Webhooks and Mini Apps. Use valid SSL certificates.
- **Secrets**: Never commit `BOT_TOKEN`. Use environment variables.
