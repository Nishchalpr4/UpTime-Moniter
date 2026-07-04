# UPtime — Uptime Monitor MVP

UPtime is a lightweight, full-stack uptime monitoring application. It periodically pings a registry of web addresses, logs response latency/HTTP status codes, and displays real-time statistics in a desaturated, high-performance dark dashboard.

---

## ⚡ 1-Line Setup

Run the following command in the project root to spin up the database, API, and frontend server:

```bash
docker compose up --build
```

- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Verification & Testing Steps

To demonstrate that the monitor correctly detects and displays both **UP** and **DOWN** states:

1. Open **[http://localhost:5173](http://localhost:5173)** in your browser.
2. Add a **Healthy URL**:
   - URL: `https://example.com`
   - Label: `Healthy Target`
   - *Result*: The request triggers an **instant synchronous ping**. The card appears immediately showing 🟢 **UP** with a response time (e.g., `124ms`) and `HTTP 200`.
3. Add a **Broken URL**:
   - URL: `https://this-domain-does-not-exist-uptime.xyz`
   - Label: `Broken Target`
   - *Result*: The card appears immediately showing 🔴 **DOWN** with `—` latency and a network timeout error message.
4. Add a **Non-2xx URL**:
   - URL: `https://httpstat.us/503`
   - Label: `Server Error Target`
   - *Result*: The card appears immediately showing 🔴 **DOWN** with a corresponding `HTTP 503` code.
5. Click **↻ Refresh** next to the logo. The button disables, changes to `Refreshing...`, fetches the latest DB states, and unlocks, providing instant visual feedback.

---

## 🏗️ System Architecture & Design Decisions

The project is structured around a **pragmatic single-file backend** and a **flat-structure frontend** to eliminate boilerplate bloat while ensuring solid multi-container coordination.

```
┌────────────────────────────────────────────────────────────────────────┐
│                              Local Docker                              │
│                                                                        │
│  ┌──────────────┐    HTTP (JSON)    ┌──────────────────────────────┐   │
│  │   Frontend   │ ────────────────► │         Backend API          │   │
│  │  React/Vite  │ ◄──────────────── │      Python + FastAPI        │   │
│  │   (:5173)    │                   │          (:8000)             │   │
│  └──────────────┘                   │                              │   │
│                                     │  ┌────────────────────────┐  │   │
│                                     │  │  Background Scheduler  │  │   │
│                                     │  │  (APScheduler Thread)  │  │   │
│                                     │  └──────────┬─────────────┘  │   │
│                                     └─────────────┼────────────────┘   │
│                                                   │ SQL Queries        │
│                                     ┌─────────────▼────────────────┐   │
│                                     │        PostgreSQL DB         │   │
│                                     │           (:5432)            │   │
│                                     └──────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Backend Design (`/backend/main.py`)
Instead of nesting database pools, route modules, and validation models into separate folders, we collapsed the entire API footprint into a single `main.py` file containing:
- **Connection Handlers**: Lightweight DB connections utilizing `psycopg2.extras.RealDictCursor`.
- **Background Pinger**: An `APScheduler` background thread executing a ping loop (`httpx.get`) on a 60-second interval with a strict 10-second timeout.
- **REST Endpoints**:
  - `GET /api/urls`: Returns registered URLs joined with their latest ping status via a `LATERAL JOIN` (eliminating N+1 query overhead).
  - `POST /api/urls`: Adds a URL and performs an **instant check** synchronously before returning, preventing UI latency state lags.
  - `DELETE /api/urls/{url_id}`: Cascades URL deletion through foreign key indexes.
  - `GET /api/urls/{url_id}/history`: Returns the last 50 checks for analytical tracking.

### 2. Database Schema (`/backend/init.sql`)
```sql
CREATE TABLE monitored_urls (
    id         SERIAL PRIMARY KEY,
    url        TEXT NOT NULL UNIQUE,
    label      TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE health_checks (
    id            SERIAL PRIMARY KEY,
    url_id        INTEGER REFERENCES monitored_urls(id) ON DELETE CASCADE,
    status        TEXT NOT NULL,            -- 'up' or 'down'
    status_code   INTEGER,                 -- e.g. 200, 503, or NULL if offline
    response_time INTEGER,                 -- ms latency or NULL if offline
    checked_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_health_checks_url_id ON health_checks(url_id);
```

### 3. Frontend Design (`/frontend/src/App.jsx` + `index.css`)
- **Dashboard UI**: Flat list displaying the status card deck. Key metric tiles (**Total**, **Up**, **Down**, **Avg Latency**) are rendered at the top to summarize health at a single glance.
- **Polling Strategy**: The page queries `/api/urls` every 30 seconds using `setInterval`, or immediately via the manual **↻ Refresh** handler.
- **Sleek Dark Theme**: Standardized on a cohesive dark slate-navy theme (`#0b0f19` bg, `#151b2c` cards) utilizing sky blue accents and low-contrast green/red badges to prevent visual exhaustion.

---

## ⚖️ Design Trade-offs & Alternatives

| Choice | Selected | Alternative | Trade-off Analysis |
|---|---|---|---|
| **API Framework** | **FastAPI** | Flask | FastAPI provides automatic Pydantic validation and `/docs` generation out of the box. Its async capability makes non-blocking concurrent requests lightweight. |
| **Scheduler** | **APScheduler** | Celery + Redis | Celery requires extra worker and message broker containers (Redis/RabbitMQ). APScheduler runs in a background thread inside the API container, keeping the deployment footprints simple. |
| **Database** | **PostgreSQL** | SQLite | While SQLite is simpler, accessing SQLite files across different container volumes can cause DB locks and file system permission issues. PostgreSQL is standard and supports robust LATERAL JOINs. |
| **Code Layout** | **Single-File** | Multi-Module | Splitting the backend into `routers/`, `schemas/`, and `database.py` adds structural overhead. A single `main.py` is faster to maintain, modify, and review. |

---

## 🌐 Production Cloud Topology (AWS ECS Fargate Sketch)

For hosting this application in production, we deploy containerized microservices to AWS using a serverless topology:

```
                  [ Internet / Route 53 ]
                             │
                             ▼
              [ Application Load Balancer ]
                ├── /api/*  ──► ECS Fargate (API Container)
                └── /*      ──► S3 Bucket + CloudFront (Static Frontend)
                                       │
                                       ▼
                         [ RDS PostgreSQL Instance ]
```

### Infrastructure-as-Code (IaC) Sketch (Terraform)

```hcl
# 1. Serverless Cluster
resource "aws_ecs_cluster" "uptime" {
  name = "uptime-cluster"
}

# 2. Managed Database (PostgreSQL)
resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.micro"
  db_name              = "uptime"
  username             = "postgres"
  password             = var.db_password
  skip_final_snapshot  = true
}

# 3. ECS Task Definition for Backend
resource "aws_ecs_task_definition" "backend" {
  family                   = "uptime-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([{
    name      = "backend"
    image     = "${var.ecr_backend_url}:latest"
    essential = true
    portMappings = [{ containerPort = 8000 }]
    environment = [
      { name = "DATABASE_URL", value = "postgresql://${aws_db_instance.postgres.username}:${var.db_password}@${aws_db_instance.postgres.endpoint}/${aws_db_instance.postgres.db_name}" }
    ]
  }])
}
```

---

## 📋 Comprehensive Development Phase Logs

We executed the system construction in the following logical sequence:

- **Phase 0: Requirement Analysis (PM)**: Defined PRD boundaries. Isolated core deliverables (CRUD API, Dashboard, Compose) from out-of-scope creep (User login, Slack notifications, SSL checks). Identified risks like dead URLs blocking scheduler loops.
- **Phase 1: Architecture (Staff Engineer)**: Mapped out framework choices (FastAPI, Postgres, APScheduler) and analyzed the trade-offs of internal threads vs distributed Celery queues.
- **Phase 2: Project Scaffold (DevOps)**: Set up the folder structures. Wrote empty dependency lists (`requirements.txt`, `package.json`) and Dockerfiles.
- **Phase 3: Backend Implementation (Backend)**: Created `init.sql` and set up endpoints in `main.py` protecting queries from SQL injections.
- **Phase 4: Background Scheduler (Backend)**: Configured the pinger loop with fallback error logging and a 10s timeout structure. Added a synchronous trigger during registration to make checks instant.
- **Phase 5: Frontend Dashboard (Frontend)**: Crafted `App.jsx` and styling files, structuring the polling state and loading behaviors.
- **Phase 6: Integration (Frontend)**: Linked frontend Axios/fetch API calls to backend endpoints, addressing CORS blocks.
- **Phase 7: Orchestration (DevOps)**: Assembled `docker-compose.yml` linking frontend, backend, and DB with pg_isready health checks.
- **Phase 8: QA & Testing (QA)**: Validated edge cases (non-2xx responses, timeouts, DNS failures) and resolved JS bugs such as handling `0ms` response times.
- **Phase 9: Pull Request Review (Reviewer)**: Cleaned up code layout, deleted dead files, and removed spinning animations from the reload triggers.
- **Phase 10: Technical Documentation (Writer)**: Compiled the `README.md` setup steps, Terraform code snippets, and `AI_LOG.md` collaboration summaries.
