# Техническое задание: AI PhotoStudio Platform (v2 — OpenRouter / без GPU)

> Версия ТЗ, которая была реализована.  
> См. также `example-ai-photostudio-tz-v1.md` для варианта с локальным GPU (InstantID).

## 1. Общая концепция

**Платформа AI PhotoStudio** — веб-сервис, где пользователь загружает свою фотографию, выбирает одну или несколько локаций (пляж, горы, город, космос, etc.) и получает сгенерированные AI фото в этих локациях с сохранением черт лица.

**AI Engine:** OpenRouter API — модель `google/gemini-*-flash-image-preview`  
**Платёжная система:** WATA Pay (https://wata.pro) — TypeScript SDK `wata-pay`

**Стек разработки:**
- Frontend: React + Vite (TypeScript)
- Backend: Hono.js + Bun
- База данных: SQLite (bun:sqlite)
- AI: OpenRouter API (HTTP из Bun, никакого Python/GPU)
- Архитектура: монорепозиторий (Turborepo)

**Ключевое преимущество:** Никакого Python, никакого GPU.  
Всё работает на чистом TypeScript/Bun. AI-генерация — это просто HTTP-запрос к OpenRouter.

---

## 2. Архитектура системы

```
Frontend (React/Vite) → Backend (Hono.js + Bun) → OpenRouter API (google/gemini-flash-image)
                                                     ↓ WATA Pay (платежи)
```

| Компонент | Технология | Сложность |
|-----------|-----------|-----------|
| Frontend | React + Vite + Tailwind | Стандартный SPA |
| Backend | Hono.js + Bun | Один процесс, без очередей |
| AI | OpenRouter API (HTTPS) | HTTP-запрос, без GPU |
| Платежи | WATA Pay SDK (npm) | 3 строки кода |
| БД | SQLite (bun:sqlite) | Файл, без сервера |

---

## 3. Пользовательские роли

### 3.1. Гость
- Может просматривать лендинг с примерами работ
- Не может генерировать без регистрации

### 3.2. Зарегистрированный пользователь
- Регистрация по email + пароль (JWT)
- Загрузка фото, выбор локаций
- 2 бесплатных генерации, далее — покупка пакета
- Оплата через WATA Pay (редирект)
- Скачивание результатов
- История генераций в личном кабинете

### 3.3. Администратор
- Дашборд: доход, пользователи, генерации
- CRUD локаций
- Управление пользователями (блокировка, баланс)
- Управление тарифами

---

## 4. Функциональные модули

### 4.1. Модуль генерации (OpenRouter API)

```typescript
// Вся AI генерация — один HTTP-запрос из Bun
const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${process.env.OPENROUTER_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "google/gemini-2.5-flash-image-preview",
    messages: [{
      role: "user",
      content: [
        { type: "text", text: locationPrompt },
        { type: "image_url", image_url: { url: `data:image/jpeg;base64,${photoBase64}` } }
      ]
    }]
  })
});
```

**Себестоимость:** ~$0.0000015 за изображение (практически ноль).

### 4.2. Каталог локаций

Промпты хранятся в БД и редактируются из админки.  
Правило: промпт начинается с глагола, описывающего трансформацию.

| Локация | Промпт |
|---------|--------|
| 🏖 Пляж на закате | "Transform this person to a tropical beach at sunset..." |
| 🗽 Нью-Йорк | "Place this person in Times Square New York City at night..." |
| 🌌 Космос | "Place this person floating in outer space..." |
| 🏰 Средневековый замок | "Place this person in a grand medieval castle hall..." |
| 🌸 Японский сад | "Place this person in a traditional Japanese garden..." |
| 🔮 Офис будущего | "Place this person in a futuristic office..." |
| 🏛 Древний Рим | "Place this person in ancient Rome..." |

### 4.3. WATA Pay

```typescript
import { WataPayApi } from "wata-pay";

const wata = new WataPayApi(process.env.WATA_API_TOKEN, "sandbox");

// Создание платёжной ссылки
const link = await wata.createLink({
  amount: 29900,        // 299₽ в копейках
  currency: "RUB",
  orderId: `${userId}_${packageId}_${Date.now()}`,
  description: "AI PhotoStudio - Стартовый",
  successRedirectUrl: `${APP_URL}/payment/success`,
  failRedirectUrl: `${APP_URL}/payment/fail`,
});

// Webhook (POST /api/webhooks/wata)
// payload: { transactionId, status: "Paid", orderId }
```

### 4.4. Тарифы

| Пакет | Цена | Генераций |
|-------|------|-----------|
| 🔹 Бесплатный | 0₽ | 2 |
| 🔸 Стартовый | 299₽ | 10 |
| 🔸 Оптимальный | 599₽ | 30 |
| 🔸 PRO | 1499₽ | 100 |

Себестоимость AI (OpenRouter): ~0.0001₽ за генерацию → маржа > 99.9%.

---

## 5. API спецификация

```
POST /api/auth/register       — Регистрация (email + password)
POST /api/auth/login          — Вход → JWT
GET  /api/auth/me             — Профиль

GET  /api/locations           — Список локаций
GET  /api/packages            — Список тарифов

POST /api/generate            — Создать генерацию (fire-and-forget, статус 202)
GET  /api/generate/:id        — Статус/результат
GET  /api/generate/history    — История пользователя

POST /api/payments/create-link  — Создать платёжную ссылку
POST /api/webhooks/wata         — Webhook от WATA

GET  /api/admin/dashboard     — Статистика
CRUD /api/admin/locations     — Управление локациями
CRUD /api/admin/packages      — Управление тарифами
GET  /api/admin/users         — Пользователи
```

---

## 6. Этапы разработки

**Phase 1 (1-2 нед):** Регистрация, загрузка фото, OpenRouter API, 7 локаций, 2 бесплатных  
**Phase 2 (1 нед):** WATA Pay, тарифы, история, скачивание  
**Phase 3 (1 нед):** Админ-панель, дашборд, управление  
**Phase 4:** Telegram-вход, пакетная генерация, кастомный промпт

---

## 7. Инфраструктура

Любой VPS (от $5/мес). GPU не нужен.  
AI: OpenRouter API (pay-as-you-go).  
Платежи: WATA Pay (комиссия за транзакцию).  
CI/CD: GitHub Actions.  

**Структура репозитория:**
```
ai-photostudio/
├── apps/
│   ├── web/          # React + Vite frontend
│   └── api/          # Hono.js + Bun backend
├── packages/
│   └── shared/       # Shared types
├── package.json      # Turborepo root
└── turbo.json
```
