# Quickstart Guide: Physical AI & Humanoid Robotics Platform

**Feature**: 001-hackathon-project-setup
**Date**: 2025-12-16

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20.x LTS | Frontend runtime |
| Python | 3.11+ | Backend runtime |
| pnpm | 8.x+ | Package manager (recommended) |
| Git | 2.x | Version control |

### Required Accounts

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| [Neon](https://neon.tech) | PostgreSQL database | Yes |
| [Qdrant Cloud](https://qdrant.tech) | Vector database | 1GB free |
| [OpenAI](https://platform.openai.com) | Embeddings & Chat | Pay-as-you-go |
| [Anthropic](https://console.anthropic.com) | Translation (Claude) | Pay-as-you-go |

---

## Quick Setup (5 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/your-org/humanoid-robotics-book.git
cd humanoid-robotics-book
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
```

**Required Environment Variables:**

```env
# Database (Neon)
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# Vector Store (Qdrant)
QDRANT_URL=https://xxx.us-east-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=your-api-key

# AI Services
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# Auth (BetterAuth)
BETTER_AUTH_SECRET=generate-a-random-32-char-string
BETTER_AUTH_URL=http://localhost:3000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Install Dependencies

```bash
# Frontend
cd website
pnpm install

# Backend
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Database Setup

```bash
# Run migrations
cd backend
python -m alembic upgrade head

# Or use raw SQL
psql $DATABASE_URL -f specs/001-hackathon-project-setup/data-model.sql
```

### 5. Index Chapters for RAG

```bash
cd backend
python scripts/index_chapters.py
```

### 6. Start Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd website
pnpm start
```

### 7. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Project Structure

```
humanoid-robotics-book/
├── website/                 # Docusaurus frontend
│   ├── docs/               # MDX chapters
│   ├── src/components/     # React components
│   └── docusaurus.config.ts
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   └── models/        # Pydantic/SQLAlchemy models
│   └── scripts/           # Utility scripts
├── specs/                   # Specifications
│   └── 001-hackathon-project-setup/
│       ├── spec.md
│       ├── plan.md
│       ├── data-model.md
│       └── contracts/     # OpenAPI schemas
└── .env.example
```

---

## Development Workflow

### Adding a New Chapter

1. Create MDX file in `website/docs/module-X/`:
   ```bash
   touch website/docs/module-1-ros/new-chapter.mdx
   ```

2. Add frontmatter:
   ```mdx
   ---
   sidebar_position: 3
   title: "New Chapter Title"
   description: "Brief description"
   ---

   # New Chapter Title

   Content here...
   ```

3. Re-index for RAG:
   ```bash
   cd backend && python scripts/index_chapters.py
   ```

### Testing the Chatbot

```bash
# Quick test via API
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a ROS 2 node?"}'
```

### Testing Authentication

```bash
# Create account
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'
```

---

## Common Issues

### "Database connection failed"
- Check `DATABASE_URL` format
- Ensure Neon project is active
- Verify SSL mode: `?sslmode=require`

### "Qdrant connection refused"
- Verify `QDRANT_URL` includes `https://`
- Check API key is correct
- Ensure collection exists (run `index_chapters.py`)

### "OpenAI rate limit"
- Check billing status
- Reduce concurrent requests
- Use `text-embedding-3-small` (cheaper)

### "Docusaurus build fails"
- Clear cache: `pnpm clear && pnpm install`
- Check Node version: `node --version` (need 20.x)

---

## Useful Commands

| Command | Description |
|---------|-------------|
| `pnpm start` | Start Docusaurus dev server |
| `pnpm build` | Build production frontend |
| `uvicorn app.main:app --reload` | Start FastAPI dev server |
| `pytest` | Run backend tests |
| `python scripts/index_chapters.py` | Re-index chapters for RAG |
| `alembic upgrade head` | Run database migrations |
| `alembic revision --autogenerate -m "desc"` | Create new migration |

---

## Agent-Specific Setup

### For Curriculum Authors
- Focus on `website/docs/` directory
- Use MDX format with React components
- Follow existing chapter structure

### For RAG Engineers
- Backend code in `backend/app/services/`
- Qdrant collection: `chapter_embeddings`
- Test with `scripts/test_rag.py`

### For Frontend Developers
- Components in `website/src/components/`
- Swizzled themes in `website/src/theme/`
- Use `pnpm start` for hot reload

---

## Next Steps

1. Run `/sp.tasks` to generate implementation task list
2. Assign tasks to appropriate agents
3. Start with P1 features (content delivery)
4. Progress through P2-P5 as time permits

---

## Support

- **Documentation**: This spec directory
- **Constitution**: `.specify/memory/constitution.md`
- **Agent Definitions**: `.claude/agents/`
