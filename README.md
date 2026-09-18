# ShopSphere — Price Comparison & Price Intelligence

> A Docker-first full-stack portfolio project for comparing electronics offers across multiple retailers and tracking price movement over time.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=111)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

## What the project does

ShopSphere is designed around a real-world price-comparison workflow:

**Discover product → compare retailer offers → choose an offer → continue to the selected retailer → complete purchase on the retailer's site.**

ShopSphere does not process the final retailer payment or delivery itself. It acts as the comparison and price-intelligence layer.

## Core features

### 🛍️ Product discovery
- Electronics catalog with categories and brands
- Search, category, brand and price filters
- Responsive product cards
- Product detail pages
- Wishlist support

### 💰 Multi-retailer comparison
- "Choose the offer you want" comparison section
- Retailer-by-retailer prices and discount percentages
- Lowest-price highlighting
- Retailer coverage and comparison snapshot
- Retailer outbound links
- Offer data model designed for SKU-level retailer URLs in production

### 📈 Price intelligence
- Historical price chart
- Marketplace selector
- Market low/current/average/spread metrics
- Store-by-store price ranges
- Trend/signal presentation

### 🔔 Price alerts
- Custom minimum/maximum target range
- PostgreSQL-backed signed-in alerts
- Local browser fallback for the demo
- Browser notification support when permitted
- Price Alerts management page
- Background market updater for demo/reference data

### 🎨 Frontend experience
- React + React Router
- Framer Motion animations
- Responsive dark cinematic interface
- Loading, empty and error states
- Animated interactions and transitions
- Production build served through Nginx

### 🧩 Backend
- FastAPI REST API
- SQLAlchemy ORM
- PostgreSQL
- Authentication and JWT-based sessions
- Wishlist and price-alert APIs
- Startup compatibility migrations for local PostgreSQL volumes
- Health endpoint: `/api/health`

## Architecture

```text
                    ┌────────────────────────┐
                    │      User Browser       │
                    │ React + Framer Motion   │
                    └───────────┬────────────┘
                                │
                         HTTP / REST API
                                │
                    ┌───────────▼────────────┐
                    │       FastAPI API       │
                    │ auth / products / user │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │      PostgreSQL 16      │
                    │ products / prices /    │
                    │ history / alerts / user│
                    └───────────▲────────────┘
                                │
                    ┌───────────┴────────────┐
                    │   Market Updater       │
                    │ demo/reference worker  │
                    └────────────────────────┘

Selected retailer offer
          │
          ▼
  Retailer product URL
          │
          ▼
  Retailer's own website
```

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React, React Router, Framer Motion, Recharts, Lucide React |
| API | FastAPI, Uvicorn, Pydantic Settings |
| Database | PostgreSQL 16, SQLAlchemy, Psycopg |
| Authentication | JWT, Passlib/Bcrypt |
| Web serving | Nginx |
| Containers | Docker Compose |
| Testing | Pytest |
| CI | GitHub Actions |

## Run locally — Docker only

### Prerequisites

- Docker Desktop
- PowerShell on Windows (or a shell on macOS/Linux)

### Start

```powershell
cd "C:\path\to\shopsphere"
docker compose up -d --build
docker compose ps
```

Open:

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API health: http://localhost:8000/api/health

### Seed/repair demo data

If the database is empty:

```powershell
docker compose exec api python -m app.services.seed
```

The API also performs compatibility checks for the local demo schema at startup.

### Stop

```powershell
docker compose down
```

Do not use `docker compose down -v` unless you intentionally want to delete the local PostgreSQL volume and all demo data.

## Retailer-link model

The frontend comparison component is intentionally separated from retailer-link generation in:

`frontend/src/lib/offers.js`

The current portfolio build uses retailer search/deep-link templates as demo behavior. For a production deployment, replace those templates with **authorized retailer/affiliate feeds containing exact SKU/ASIN/model identifiers and canonical product URLs**.

This distinction matters: a retailer homepage or generic search page is not the same thing as an exact product detail page.

## Demo-data disclaimer

Prices, discounts and historical movement in this portfolio project are **demo/reference data**. They are not claimed to be live retailer prices.

A production system should use permitted retailer APIs, affiliate feeds, partner feeds or other authorized sources, then normalize products by stable identifiers before presenting exact retailer offers.

## Project structure

```text
shopsphere/
├── backend/
│   ├── app/
│   │   ├── api/              # REST endpoints
│   │   ├── core/             # configuration/security
│   │   ├── db/               # database session
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # API schemas
│   │   └── services/         # seed + market updater
│   ├── migrations/           # compatibility SQL
│   ├── tests/                # backend tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── pages/
│   │   └── styles.css
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── .github/workflows/ci.yml
├── docker-compose.yml
├── .env.example
├── LICENSE
└── README.md
```

## CI/CD

GitHub Actions runs on pushes and pull requests and checks:

1. Python compilation
2. Backend dependency installation
3. Frontend dependency installation
4. Production frontend build

Workflow: `.github/workflows/ci.yml`

## Security notes

- Never commit `.env` or production secrets.
- Replace the development `SECRET_KEY` before deployment.
- Use HTTPS in production.
- Use managed PostgreSQL/backups for production.
- Add rate limiting, secret management, stronger CORS rules and production observability before public deployment.

See `SECURITY.md` for the portfolio project's security expectations.

## Portfolio positioning

This project demonstrates practical full-stack skills rather than only UI work:

- REST API design
- Relational data modeling
- Authentication
- Search/filtering
- Price comparison
- Historical analytics
- Background processing
- Browser notifications
- Dockerized development/deployment
- CI automation
- Production-oriented architecture decisions

## License

MIT — see `LICENSE`.
