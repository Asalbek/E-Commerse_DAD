# FlashCart — Real-Time E-Commerce & Flash Sale Platform

FlashCart is a high-performance, polyglot e-commerce system designed to handle real-time inventory management and high-concurrency flash sales. Built for a university-level Database Application and Design project (Spring 2026), it demonstrates advanced distributed systems concepts, polyglot persistence, and unified observability.

## 🚀 Key Features
- **Atomic Flash Sales**: Sub-millisecond stock decrements using Redis atomic operations.
- **Polyglot Storage**: PostgreSQL for transactions, Redis for caching/rate-limiting, and Elasticsearch for fuzzy search.
- **Asynchronous Pipeline**: 3-stage order fulfillment processed via RabbitMQ.
- **Real-Time Inventory**: Live stock pushes to the frontend via WebSockets and Redis Pub/Sub.
- **Observability Stack**: Full visibility with Prometheus (metrics), Loki (logs), and Tempo (tracing).
- **Custom Algorithms**: Hand-built 64-bit Snowflake ID generator and Token-Bucket rate limiter.

## 🛠 Tech Stack
| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, Vanilla CSS |
| **Backend** | FastAPI (Python 3.11), SQLAlchemy, Alembic |
| **Primary DB** | PostgreSQL 16 |
| **Cache/KV** | Redis 7 |
| **Search** | Elasticsearch 8.13 |
| **Broker** | RabbitMQ 3.13 |
| **Gateway** | Nginx |
| **Monitoring** | Grafana, Prometheus, Loki, Tempo, Promtail |

## 📦 Getting Started

### Prerequisites
- Docker and Docker Compose
- 4GB+ RAM (Elasticsearch requirement)

### One-Command Start
```bash
docker compose up -d
```
Wait approximately 60 seconds for health checks to pass.

### Access Points
- **Storefront**: [http://localhost](http://localhost)
- **API Documentation**: [http://localhost/docs](http://localhost/docs)
- **Grafana Dashboards**: [http://localhost:3001](http://localhost:3001) (User: `admin`, Pass: `admin`)
- **RabbitMQ Management**: [http://localhost:15672](http://localhost:15672)

## 🏗 Architecture
FlashCart uses a microservices-inspired architecture with 15 containers.
- **Nginx** load-balances traffic across two **FastAPI** backend replicas.
- **Workers** handle background order processing and batch settlements.
- **Promtail** scrapes logs from all containers and ships them to **Loki**.

## 📖 Requirements Audit
This project fulfills all 13 project requirements (R1-R13), including:
- **R11 (From-Scratch)**: Custom Snowflake ID and Token-Bucket Rate Limiter.
- **R7 (Non-REST)**: WebSocket-based inventory updates.
- **R10 (Pipeline)**: 3-stage RabbitMQ stream processing.

## ⚖️ License
This project was developed for academic purposes.
