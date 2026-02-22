---
name: trading212
description: Interact with Trading 212 investment account. Use when the user asks about portfolio, positions, balance, orders, dividends, transactions, or wants to place/cancel trades. Triggers on keywords like "trading 212", "portfolio", "positions", "balance", "stocks", "investments", "buy", "sell", "order".
metadata:
  {
    "openclaw":
      {
        "emoji": "📈",
        "requires":
          {
            "env": ["TRADING212_API_KEY_ID", "TRADING212_SECRET_KEY"],
          },
      },
  }
---

# Trading 212

Full API client for Trading 212 (Invest & Stocks ISA accounts).

## Setup

Credentials are stored in `/workspace/.trading212-config.json`:

```json
{
  "apiKeyId": "YOUR_API_KEY_ID",
  "secretKey": "YOUR_SECRET_KEY",
  "environment": "live"
}
```

## Authentication

Uses HTTP Basic Auth: `API_KEY_ID` as username, `SECRET_KEY` as password.

## Running

```bash
node /workspace/skills/trading212/dist/trading212.js <command>
```

## Commands

### Account
| Command | Description | Rate Limit |
|---------|-------------|------------|
| `summary` | Full account summary (balance, investments, P&L) | 1 req / 5s |
| `cash` | Cash balance details | 1 req / 5s |

### Positions
| Command | Description | Rate Limit |
|---------|-------------|------------|
| `positions` | All open positions with P&L | 1 req / 1s |
| `position <ticker>` | Single position details | 1 req / 1s |

### Orders
| Command | Description | Rate Limit |
|---------|-------------|------------|
| `orders` | All pending orders | 1 req / 5s |
| `order <id>` | Get order by ID | 1 req / 5s |
| `cancel <id>` | Cancel pending order | 1 req / 5s |
| `buy-market <ticker> <qty>` | Place market buy | 1 req / 1s |
| `sell-market <ticker> <qty>` | Place market sell | 1 req / 1s |
| `buy-limit <ticker> <qty> <price>` | Place limit buy | 1 req / 1s |
| `sell-limit <ticker> <qty> <price>` | Place limit sell | 1 req / 1s |
| `buy-stop <ticker> <qty> <stopPrice>` | Place stop buy | 1 req / 1s |
| `sell-stop <ticker> <qty> <stopPrice>` | Place stop sell | 1 req / 1s |
| `buy-stop-limit <ticker> <qty> <stop> <limit>` | Place stop-limit buy | 1 req / 1s |
| `sell-stop-limit <ticker> <qty> <stop> <limit>` | Place stop-limit sell | 1 req / 1s |

### Historical
| Command | Description | Rate Limit |
|---------|-------------|------------|
| `history-orders` | Past executed orders | 1 req / 5s |
| `dividends` | Dividend payments received | 1 req / 5s |
| `transactions` | Cash transactions (deposits, withdrawals) | 1 req / 5s |
| `reports` | List generated CSV reports | 1 req / 5s |

### Instruments
| Command | Description | Rate Limit |
|---------|-------------|------------|
| `instruments` | All tradable instruments | 1 req / 50s |
| `exchanges` | Available exchanges and schedules | 1 req / 30s |

## Important Notes

- **Sell orders use negative quantities** — the CLI handles this automatically
- **Orders execute in primary account currency only**
- **Multi-currency accounts not supported** via API
- **Rate limits are per-account**, not per-key
- Environments: `live` (real money) or `demo` (paper trading)

## Safety

- **NEVER place orders without explicit user confirmation**
- Always show order details before executing
- For sell orders, verify the position exists first
- Monitor rate limit headers to avoid being blocked

## Programmatic Usage

```typescript
import { Trading212Client } from './trading212';

const client = Trading212Client.fromFile();
const summary = await client.getAccountSummary();
const positions = await client.getPositions();
const orders = await client.getPendingOrders();
```
