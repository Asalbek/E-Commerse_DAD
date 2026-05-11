# Changelog

All notable changes to FlashCart will be documented in this file.

## [1.0.0] - 2026-05-10

### Added
- Full e-commerce platform with product catalogue, cart, and checkout
- Real-time inventory tracking via WebSocket
- Flash-sale system with atomic stock decrement (Redis)
- Full-text product search with Elasticsearch
- Order processing pipeline via RabbitMQ
- Daily settlement batch job
- Snowflake ID generator (from-scratch)
- Token-bucket rate limiter (from-scratch)
- JWT authentication with role-based access
- Admin dashboard for product and flash-sale management
- Nginx API gateway with load balancing (2 backend replicas)
- Full observability stack: Prometheus, Grafana, Loki, Tempo
- Docker Compose orchestration for all services
- OpenAPI/Swagger interactive documentation
- Alembic database migrations with seed data
