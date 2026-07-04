# UPtime — Lightweight Full-Stack Uptime Monitor MVP

A self-contained, high-performance URL health monitor featuring a synchronous initial check loop, a background cron pinger, and a sleek, desaturated dark dashboard.

---

## 🚀 1-Line Setup & Local Execution

- **Prerequisite**: Docker Desktop running.
- **Run Stack** (Execute in project root):
  ```bash
  docker compose up --build
  ```
- **Access Endpoints**:
  - Dashboard: [http://localhost:5173](http://localhost:5173)
  - Interactive API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
- **Stop Stack**:
  ```bash
  docker compose down
  ```

---

## 🧪 Testing Verification

Open **[http://localhost:5173](http://localhost:5173)** and add these endpoints to test:
- **Active State**: Add `https://example.com` ──► Instantly displays 🟢 **UP** (with ms latency).
- **Network Failure**: Add `https://nonexistent-url-target.xyz` ──► Instantly displays 🔴 **DOWN** (with `—` latency).
- **HTTP Status Failure**: Add `https://httpstat.us/503` ──► Instantly displays 🔴 **DOWN** (showing `HTTP 503`).

---

## 🏗️ System Architecture & Data Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor User as User/Browser
    participant UI as React UI (5173)
    participant API as FastAPI (8000)
    participant DB as Postgres DB (5432)
    participant Scheduler as Background Pinger

    User->>UI: Add URL (https://example.com)
    UI->>API: POST /api/urls
    Note over API: Triggers ping_one() synchronously
    API->>DB: INSERT status & latency
    API-->>UI: Return created URL (UP/DOWN)
    
    loop Every 60 seconds
        Scheduler->>DB: Fetch URLs
        Scheduler->>User: Pings HTTP endpoints (10s timeout)
        Scheduler->>DB: INSERT check results (latency, status, code)
    end

    loop Every 30 seconds
        UI->>API: GET /api/urls (Lateral Join)
        API->>DB: Query URLs + Latest Health Check
        DB-->>API: URL list with current states
        API-->>UI: Return JSON
        UI->>User: Update Dashboard Stats & List
    end
```

---

## ⚖️ Technology Trade-offs

| Choice | Selected | Rejected Alternative | Why Selected |
|---|---|---|---|
| **Web API** | **FastAPI** | Flask / Express | Async performance, Pydantic validation models, auto-docs. |
| **Scheduler** | **APScheduler** | Celery + Redis | Thread-based in-process execution; avoids Redis/worker containers. |
| **Database** | **PostgreSQL** | SQLite | Safe concurrent writes across shared volumes; no Docker file locks. |
| **Architecture** | **Single-file** | Multi-Module Layout | Merged into `main.py` (~150 lines) to eliminate directory overhead. |

---

## 🤖 AI-Driven Development Loop (Cursor + Claude 3.5 Sonnet)

To achieve maximum execution velocity, the entire environment was built using **Cursor IDE powered by Claude 3.5 Sonnet** as a unified AI engineering agent.

### 1. AI Tool Selection Trade-offs

```mermaid
graph TD
    Start([Need AI Developer Assistant]) --> Workflow{Primary Goal?}
    
    Workflow -->|Multi-file edits & terminal control| Chosen[Cursor + Claude 3.5 Sonnet]
    Workflow -->|Simple line autocomplete| Copilot[GitHub Copilot]
    Workflow -->|General Q&A / Copy-paste| Web[ChatGPT / Claude Web]

    style Chosen fill:#064e3b,stroke:#34d399,stroke-width:3px,color:#fff
    style Copilot fill:#0f172a,stroke:#64748b,color:#fff
    style Web fill:#0f172a,stroke:#64748b,color:#fff
```

| Tool Choice | Why Selected Over Alternatives |
|---|---|
| **Cursor + Claude 3.5 Sonnet** <br>*(Chosen)* | **Selected** because the logical reasoning of Sonnet combined with Cursor's ability to index folder contexts and execute shell commands inside the terminal allowed the scaffolding, building, and debugging of the entire stack in minutes. |
| **GitHub Copilot** <br>*(Rejected)* | **Rejected** because it is limited to line-by-line autocompletion and lacks the cross-file reasoning needed to write database schemas and configure Docker files. |
| **ChatGPT / Claude Web** <br>*(Rejected)* | **Rejected** because copy-pasting code between browser chats and local files introduces high friction and increases the risk of sync errors. |

---

### 2. The 4-Step Scaffolding Methodology

```mermaid
graph LR
    Plan[1. Scope & Design] -->|Claude Opus| Dev[2. Backend & Pinger]
    Dev -->|Cursor IDE| UI[3. Frontend & UX]
    UI -->|Vite / Slate CSS| Ship[4. Deploy & QA]

    style Plan fill:#0b0f19,stroke:#38bdf8,stroke-width:2px,color:#fff
    style Dev fill:#0b0f19,stroke:#34d399,stroke-width:2px,color:#fff
    style UI fill:#0b0f19,stroke:#8b5cf6,stroke-width:2px,color:#fff
    style Ship fill:#064e3b,stroke:#34d399,stroke-width:3px,color:#fff
```

- **1. Scope & Design**: Analyzed specs, isolated PRD scope boundaries, and resolved the database selection (Postgres vs SQLite volume lock risks).
- **2. Backend & Pinger**: Scaffolded FastAPI CRUD, parameterized SQL inserts, and isolated the APScheduler background pinger thread with 10s timeouts.
- **3. Frontend & UX**: Generated the React dashboard, set 30s polling, and implemented synchronous checks inside the POST endpoint for instant UI updates.
- **4. Deploy & QA**: Configured Docker Compose network dependencies and patched JS metrics bugs (resolving `0ms` response times truthy checks).

---

## 🌐 Production Cloud Topology (AWS)

```mermaid
graph LR
    Browser[User Browser] --> Route53[Route 53] --> ALB[Application Load Balancer]
    ALB -->|/*| S3[S3 Static Frontend]
    ALB -->|/api/*| ECS[ECS Fargate API Containers]
    ECS --> RDS[(RDS PostgreSQL DB)]

    style Browser fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff
    style S3 fill:#1e293b,stroke:#38bdf8,color:#fff
    style ECS fill:#1e293b,stroke:#38bdf8,color:#fff
    style RDS fill:#1e293b,stroke:#38bdf8,color:#fff
```

### Hypothetical Terraform (IaC) Configuration
```hcl
resource "aws_ecs_cluster" "uptime" { name = "uptime" }

resource "aws_db_instance" "postgres" {
  allocated_storage = 20
  engine            = "postgres"
  instance_class    = "db.t3.micro"
  db_name           = "uptime"
  username          = "postgres"
  password          = var.db_password
  skip_final_snapshot = true
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "uptime-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  container_definitions    = jsonencode([{
    name  = "backend"
    image = "${var.ecr_url}:latest"
    portMappings = [{ containerPort = 8000 }]
    environment  = [{ name = "DATABASE_URL", value = "postgresql://postgres:${var.db_password}@${aws_db_instance.postgres.endpoint}/uptime" }]
  }])
}
```
