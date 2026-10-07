# VoiceOS AWS Production Architecture & Deployment Runbook

Per VoiceOS BRAIN §52:

```text
AWS
 │
 ├── ECS / Fargate (Container Tasks: API & Voice Worker)
 ├── Application Load Balancer (ALB with TLS 443 termination)
 ├── RDS PostgreSQL (Multi-AZ for ACID order persistence)
 ├── ElastiCache Redis (In-memory session state & locks)
 ├── S3 (Audio recordings, call logs, model artifacts)
 ├── Secrets Manager (LLM, STT, TTS, LiveKit credentials)
 └── CloudWatch (OpenTelemetry distributed metrics and alerts)
```

## 1. Secrets Configuration
Store external service keys in AWS Secrets Manager:
- `GEMINI_API_KEY`
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- `DEEPGRAM_API_KEY`
- `CARTESIA_API_KEY`
- `DATABASE_URL`
- `REDIS_URL`

## 2. Infrastructure as Code Guidelines
Deploy using AWS ECS Fargate or Terraform with:
- Task Definition: 2 vCPU, 4GB RAM minimum per worker container.
- Health check path: `/api/v1/health`
- Sticky sessions disabled on ALB (stateless REST APIs).
- LiveKit connects via secure WebSockets (`wss://`).
