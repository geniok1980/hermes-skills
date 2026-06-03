# WATA Pay Integration Reference

WATA Pay — платёжный сервис для международного бизнеса (https://wata.pro)

## SDK

**TypeScript SDK:** `wata-pay` (runtime-agnostic: Node 18+, Bun, Deno)

```bash
npm install wata-pay
bun add wata-pay
deno add jsr:@omnifaced/wata-pay
```

Zero dependencies — uses global `fetch` and `Web Crypto` APIs.

## Quick Start

```typescript
import { WataPayApi } from "wata-pay";

const api = new WataPayApi("your-bearer-token");

// Create a payment link
const link = await api.createLink({
  amount: 1500,      // in kopecks/cents (1500 = 15₽)
  currency: "RUB",
  orderId: "order-42",
  description: "Premium subscription",
  successRedirectUrl: "https://example.com/success",
  failRedirectUrl: "https://example.com/fail",
  expirationDateTime: "2026-12-31T23:59:59Z", // optional
});

console.log(link.url);

// Get transaction status
const transaction = await api.getTransaction("transaction-id");
```

## Sandbox Mode

```typescript
const api = new WataPayApi("your-sandbox-token", "sandbox");
```

## API Methods

### Payment Links

```typescript
// Create
api.createLink({ amount, currency, orderId, type?, description?, successRedirectUrl?, failRedirectUrl?, expirationDateTime? })

// Get single
api.getLink("link-id")

// Search
api.getLinks({ currencies?, statuses?, sorting?, maxResultCount? })
```

### Transactions

```typescript
// Get single
api.getTransaction("transaction-id")

// Search
api.getTransactions({ statuses?, amountFrom?, ... })
```

## Webhook

Endpoint: `POST /api/webhooks/wata`

Payload: `{ transactionId, status: "Paid"|"Pending"|"Failed"|"Expired", orderId }`

### Handling flow:
1. Receive webhook
2. Validate signature (if provided)
3. Extract userId + packageId from orderId
4. If status === "Paid" → grant generations to user
5. Return 200 OK

## Integration with Bun

```typescript
// In Hono.js + Bun
import { Hono } from "hono";
import { WataPayApi } from "wata-pay";

const app = new Hono();
const wata = new WataPayApi(process.env.WATA_API_TOKEN);

app.post("/api/payments/create-link", async (c) => {
  const { packageId } = await c.req.json();
  const user = c.get("user");
  
  const link = await wata.createLink({
    amount: package.price,
    currency: "RUB",
    orderId: `${user.id}_${packageId}_${Date.now()}`,
    description: `AI PhotoStudio - ${package.name}`,
    successRedirectUrl: `${FRONTEND_URL}/payment/success`,
    failRedirectUrl: `${FRONTEND_URL}/payment/fail`,
  });
  
  return c.json({ url: link.url, id: link.id });
});
```

## ⚠️ Price Unit: What WATA Expects

The WATA SDK `createLink({ amount })` — WATA docs don't clearly state the unit.  
From the SDK quick-start example:

```typescript
amount: 1500,
currency: "RUB",
```

This likely means **kopecks** (1500 = 15.00₽), but verify against WATA's current spec.

**In the seed data, prices are stored in rubles** (299 = 299₽).  
If WATA expects kopecks, multiply by 100 before sending:
```
await wata.createLink({ amount: priceInRubles * 100, ... })
```

If WATA expects rubles, send as-is. **Test in sandbox first** to confirm.

## Pricing Tiers (example)

| Package | Price | Generations |
|---------|-------|-------------|
| Free (once) | 0₽ | 2 (watermarked) |
| Starter | 299₽ | 10 |
| Optimal | 599₽ | 25 |
| PRO | 1499₽ | 100 |

Send amount in **kopecks** to WATA: 299₽ = 29900
