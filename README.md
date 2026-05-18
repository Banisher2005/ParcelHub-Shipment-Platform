# ParcelHub — Universal Shipment Tracking Platform

A production-grade shipment tracking hub that normalizes tracking data from multiple carriers into a single, premium dashboard.

![ParcelHub](https://img.shields.io/badge/ParcelHub-v0.1.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue)

## Features

- 📦 **Universal tracking** — Paste any tracking number, auto-detect the carrier
- 🔄 **Auto-refresh** — Background polling for API-trackable carriers
- ✏️ **Manual tracking** — Support for Amazon, Flipkart, and custom carriers
- 🎨 **Premium UI** — Dark-first design inspired by Linear and Arc
- 📊 **Dashboard** — Stats, filters, search, and animated cards
- 📍 **Timeline** — Beautiful vertical tracking timeline with events
- 🏷️ **Labels** — Custom labels for easy identification
- 🔌 **Provider abstraction** — Never coupled to any single tracking API

## Supported Carriers

### API-Trackable (Auto-refresh)
Delhivery • BlueDart • India Post • DHL • FedEx • UPS • YunExpress • Cainiao • Yanwen • 4PX

### Manual-Only (User updates)
Amazon • Flipkart • Custom carriers

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, TailwindCSS v4, Framer Motion, TanStack Query, Zustand |
| Backend | FastAPI, Python 3.12+, SQLAlchemy async, Pydantic v2 |
| Database | SQLite (dev), PostgreSQL-ready |
| Tracking | 17TRACK API (via provider abstraction layer) |

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` — the frontend proxies API calls to `localhost:8000`.

## Architecture

```
Frontend (Next.js)
  → API Client
  → Internal REST API (/api/v1)
  → Service Layer
  → Repository Layer → Database
  → Provider Layer → 17TRACK / Mock / Future providers
```

The provider abstraction ensures we're **never coupled** to any single tracking API. Swap providers with zero frontend changes.

## Project Structure

```
parcelhub/
├── backend/
│   └── app/
│       ├── api/v1/          # Route handlers
│       ├── core/            # Config, logging
│       ├── db/              # Engine, session
│       ├── models/          # SQLAlchemy ORM
│       ├── schemas/         # Pydantic DTOs
│       ├── repositories/    # Data access
│       ├── services/        # Business logic
│       ├── providers/       # Tracking provider abstraction
│       └── tasks/           # Background polling
├── frontend/
│   └── src/
│       ├── app/             # Next.js pages
│       ├── components/      # React components
│       ├── hooks/           # TanStack Query hooks
│       ├── lib/             # API client, utils
│       ├── stores/          # Zustand state
│       └── types/           # TypeScript types
└── README.md
```

## License

MIT
