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

## 🏗️ System Architecture & Data Flow

```mermaid
graph TD
    User([User]) -->|1. Register URL| UI[React UI]
    UI -->|2. POST request| API[FastAPI API]
    API -->|3. Initial synchronous ping| DB[(PostgreSQL)]
    
    Scheduler[Background Pinger] -->|4. Ping checks every 60s| Websites[Target Sites]
    Scheduler -->|5. Log health check results| DB

    UI -->|6. Polling update requests every 30s| API
    API -->|7. Fetch current states| DB

    style User fill:#0b0f19,stroke:#38bdf8,stroke-width:2px,color:#fff
    style UI fill:#151b2c,stroke:#38bdf8,color:#fff
    style API fill:#151b2c,stroke:#38bdf8,color:#fff
    style DB fill:#151b2c,stroke:#38bdf8,color:#fff
    style Scheduler fill:#151b2c,stroke:#34d399,color:#fff
    style Websites fill:#151b2c,stroke:#64748b,color:#fff
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

## 🤖 My AI-Driven Development Loop (Cursor + Claude Opus 4.6)

To achieve maximum execution velocity, the entire environment was built using **Cursor IDE powered by Claude Opus 4.6** as a unified AI engineering agent.

### 1. Parallel Multi-Agent Scaffolding Loop
I directed Claude Opus 4.6 to run validation check gates first, spawn parallel development loops for separate components, configure Dockerfiles on each end, and combine them into a single compose file:

```mermaid
graph TD
    PRD[1. PRD Define & Validation: Claude Opus 4.6] -->|Dispatched Parallel Agents| Parallel{Parallel Build Stage}
    
    Parallel -->|Agent A: Backend API| Backend[Backend Development<br>• main.py CRUD API<br>• backend/Dockerfile]
    Parallel -->|Agent B: Frontend UI| Frontend[Frontend Development<br>• React App.jsx & styles<br>• frontend/Dockerfile]
    Parallel -->|Agent C: Background Scheduler| Scheduler[Scheduler & DB Setup<br>• APScheduler Thread<br>• Postgres init.sql schema]
    
    Backend -->|System Integration| Combine[Final Docker Compose Conductor]
    Frontend -->|System Integration| Combine
    Scheduler -->|System Integration| Combine

    Combine -->|Network & Volume Orchestration| Ship[Ship MVP 🚀]

    style PRD fill:#0b0f19,stroke:#38bdf8,stroke-width:2px,color:#fff
    style Parallel fill:#0b0f19,stroke:#f59e0b,stroke-width:2px,color:#fff
    style Backend fill:#151b2c,stroke:#8b5cf6,stroke-width:2px,color:#fff
    style Frontend fill:#151b2c,stroke:#8b5cf6,stroke-width:2px,color:#fff
    style Scheduler fill:#151b2c,stroke:#8b5cf6,stroke-width:2px,color:#fff
    style Combine fill:#0b0f19,stroke:#34d399,stroke-width:2px,color:#fff
    style Deploy fill:#064e3b,stroke:#34d399,stroke-width:3px,color:#fff
```

**My Tool Choice**: I selected **Cursor IDE (powered by Claude Opus 4.6)** as my single, unified AI coding agent. The deep logic reasoning of Claude Opus 4.6 combined with Cursor's ability to index folder contexts and execute shell commands inside the terminal allowed the scaffolding, building, and debugging of the entire stack in minutes without leaving my editor.

---

### 2. My Agentic Lifecycle & Implementation Loop

I drove the development process by guiding the Cursor agent through a structured 4-stage lifecycle:
- **1. PRD Define**: I analyzed the specifications and directed the agent to isolate constraints (e.g. timeout logic) to set a clear MVP scope boundary before generating code.
- **2. Harness Engineering**: I set up the environment files and folders. I had the agent generate empty configurations (`requirements.txt`, `package.json`, and Docker compose skeletons) to verify network ports and DB connections before writing logic.
- **3. Multi-Agent Deploy**: I executed parallel milestones. I directed the agent to concurrently construct the Postgres database schemas (`init.sql`), code the backend CRUD routes (`main.py`), and generate the dashboard components (`App.jsx`).
- **4. System Integration**: I wired the API and UI layers. I bypassed local Windows script locks by manual bootstrapping, resolved CORS blocks, and refactored the POST route to ping target URLs synchronously for instant status updates.

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
