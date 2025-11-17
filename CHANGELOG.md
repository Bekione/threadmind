# ThreadMind Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-11-17

summarize` commands
- 📝 AI-powered thread summarization (OpenAI & Gemini support)
- ⭐ Intelligent highlight extraction from discussions
- 💾 PostgreSQL persistence for jobs and users
- 🔄 Celery async worker pool for scalable processing
- 🚀 Horizontal scaling support (multi-worker deployment)
- 🔐 Rate limiting per user (Redis-backed)
- 📊 Structured JSON logging
- 🐳 Docker Compose setup with migrate, API, worker, bot, Redis, Postgres
- 🧪 Full test coverage for API endpoints
- 📱 Forwarded post detection and URL parsing
- 💰 Token usage and cost tracking

### Features
- **API Endpoints**:
  - `POST /ingest` - Submit thread for summarization
  - `GET /result/{job_id}` - Poll job status and results
  - `GET /healthz` - Health check
  - `GET /` - Root endpoint

- **Bot Commands**:
  - `/start` - Welcome message with usage instructions
  - `/help` - Detailed help and tips
  - `/summarize <url>` - Summarize a specific thread
  - Forward posts - Auto-detect and summarize

- **Configuration**:
  - Environment-based settings
  - Telegram API credentials (Telethon)
  - AI provider selection (OpenAI/Gemini)
  - Rate limiting thresholds
  - Database and Redis URLs

### Built by
@Groots23

---

## Future Versions

### [1.1.0] - Planned
- Webhook mode for bot (instead of polling)
- Batch thread summarization
- Result caching (24h TTL)
- User preferences (summary length, language, tone)
- Analytics dashboard
- Admin panel

### [1.2.0] - Planned
- Multi-language support
- Custom AI prompt templates
- Thread comparison (summarize multiple threads)
- Export to PDF/JSON
- Slack integration

