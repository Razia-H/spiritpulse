# 🥃 SpiritPulse

**Alcohol Industry Social Analytics Pipeline**

A production-grade data pipeline that ingests simulated social media data about alcohol brands, transforms it with dbt, stores it in Railway Postgres, and exposes insights via a FastAPI backend with a live dashboard.

Built as a portfolio project demonstrating AI-forward data engineering.

---

## Architecture

```
Social Simulator → DLT → Railway Postgres (raw) → dbt → analytics marts → FastAPI → Dashboard
```

| Layer | Technology | Purpose |
|---|---|---|
| Ingestion | Python + DLT | Simulates social API, loads to Postgres |
| Transformation | dbt-postgres | Staging views + analytics mart tables |
| Storage | Railway Postgres | `spiritpulse` schema, isolated from other projects |
| API | FastAPI + SQLAlchemy async | REST endpoints with Pydantic models |
| Dashboard | HTML + Chart.js | Live charts and sentiment tables |

## Brands Tracked

Jack Daniel's · Modelo · Guinness · Hendrick's Gin · Don Julio · Whispering Angel

---

## Setup

### 1. Clone and install

```powershell
git clone https://github.com/Razia-H/spiritpulse
cd spiritpulse
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env` and set your Railway connection string:

```
DATABASE_URL=postgresql://postgres:password@host:port/railway
DATABASE_SCHEMA=spiritpulse
```

### 3. Run the full pipeline

```powershell
.\scripts\run_pipeline.ps1
```

This runs ingestion → dbt → starts the API.

### 4. Open the dashboard

Open `dashboard/index.html` in your browser.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/brands` | List all tracked brands |
| GET | `/brands/{id}` | Get single brand |
| GET | `/sentiment` | All brands sentiment (last 7 days) |
| GET | `/sentiment/{brand_id}` | Brand sentiment history |
| GET | `/sentiment/{brand_id}/summary` | Aggregated brand summary |
| GET | `/trends` | Top trending hashtags |
| GET | `/trends/{brand_id}` | Brand-specific hashtag trends |
| GET | `/health` | API + DB health check |

Full interactive docs at **http://localhost:8000/docs**

---

## dbt Models

```
models/
├── staging/
│   ├── stg_posts.sql        — cleaned posts view
│   └── stg_brands.sql       — cleaned brands view
└── marts/
    ├── mart_brand_sentiment.sql    — daily sentiment aggregates
    └── mart_trending_hashtags.sql  — top 20 hashtags per day
```

---

## AI-Forward Workflow

This project was built using an AI-forward engineering approach:

1. **Razia designed** the architecture and wrote specifications for each layer
2. **Claude implemented** the code from those specifications
3. **Razia validated** correctness, ran tests, and shipped

This mirrors the workflow at companies transitioning from AI-assisted to AI-forward development.

---

## Author

**Razia H** — [github.com/Razia-H](https://github.com/Razia-H)
