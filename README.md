# SpiritPulse

> Alcohol industry social analytics pipeline - built with an AI-forward engineering workflow.

## Demo

https://github.com/Razia-H/spiritpulse/blob/main/assets/demo.mp4

## Architecture

```\nSocial Simulator -> DLT -> Railway Postgres (raw) -> dbt -> analytics marts -> FastAPI -> Dashboard\n```\n
| Layer | Technology | Purpose |
|---|---|---|
| Ingestion | Python + DLT | Simulates social API, loads to Postgres |
| Transformation | dbt-postgres | Staging views + analytics mart tables |
| Storage | Railway Postgres | Isolated spiritpulse schema |
| API | FastAPI + SQLAlchemy | REST endpoints with Pydantic models |
| Dashboard | HTML + Chart.js | Live charts and sentiment tables |

## Brands Tracked

Jack Daniel's - Modelo - Guinness - Hendrick's Gin - Don Julio - Whispering Angel

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /brands | List all tracked brands |
| GET | /sentiment | All brands sentiment last 7 days |
| GET | /sentiment/{brand_id} | Brand sentiment history |
| GET | /trends | Top trending hashtags |
| GET | /health | API and DB health check |

## AI-Forward Workflow

1. Razia designed the architecture and wrote specs for each layer
2. Claude implemented the code from those specifications
3. Razia validated correctness and shipped

## Author

Razia H - https://github.com/Razia-H
