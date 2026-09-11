# TAZERIS paid API tools for AI agents

TAZERIS also exposes small machine-to-machine API tools through the public App Factory gateway. These endpoints use the x402 payment protocol on Base and show their price before settlement. They do not require a call or manual delivery.

## Service discovery

- Agent/x402 manifest: https://tazeris-app-factory-production.up.railway.app/.well-known/x402
- Service health: https://tazeris-app-factory-production.up.railway.app/x402/health

## Paid API endpoints

- `POST https://tazeris-app-factory-production.up.railway.app/paid/json-review` — JSON quality review — $0.05
- `POST https://tazeris-app-factory-production.up.railway.app/paid/json-normalize` — canonical JSON normalization — $0.03
- `POST https://tazeris-app-factory-production.up.railway.app/paid/text-analyze` — deterministic text statistics — $0.03

The exact payment requirements are returned by the x402 flow before settlement. Do not send secrets, credentials, personal records, or other sensitive data to public demo/API endpoints.

## Other TAZERIS services

- Website repair from €49: https://tazeris-money-factory-production.up.railway.app/services/website-fix?utm_source=github&utm_medium=agent_tools&utm_campaign=tazeris_network
- Telegram Bot MVP from €79: https://tazeris-money-factory-production.up.railway.app/services/telegram-bot?utm_source=github&utm_medium=agent_tools&utm_campaign=tazeris_network
- Android MVP from €149: https://tazeris-money-factory-production.up.railway.app/services/android-mvp?utm_source=github&utm_medium=agent_tools&utm_campaign=tazeris_network
- Live Telegram bot catalog: https://tazeris-bot-factory-production.up.railway.app/bots?utm_source=github&utm_medium=agent_tools&utm_campaign=tazeris_network
