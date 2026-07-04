# UPtime — Uptime Monitor MVP

A simple, containerized full-stack URL monitor that checks website status, logs response times, and displays results in a dark slate dashboard.

---

## 🏗️ System Architecture

```mermaid
graph LR
    User([User Browser]) <--> UI[React UI]
    UI <--> API[FastAPI API]
    API <--> DB[(PostgreSQL)]
    Scheduler[Background Pinger] -.->|Ping every 60s| Target[Websites]
    Scheduler -.->|Save logs| DB

    style User fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff
    style UI fill:#1e293b,stroke:#38bdf8,color:#fff
    style API fill:#1e293b,stroke:#38bdf8,color:#fff
    style DB fill:#1e293b,stroke:#38bdf8,color:#fff
    style Scheduler fill:#1e293b,stroke:#34d399,color:#fff
    style Target fill:#1e293b,stroke:#64748b,color:#fff
```

### Setup & Verification
1. **Launch Stack**: `docker compose up --build`
2. **Access Dashboard**: Open `http://localhost:5173`.
3. **Verify UP/DOWN**:
   - Add `https://example.com` (shows 🟢 **UP** instantly).
   - Add `https://broken-target-test.xyz` (shows 🔴 **DOWN** instantly).

---

## ⚖️ My Technology Trade-offs

I made the following design decisions based on project constraints and performance requirements:

- **I chose FastAPI over Flask/Express**: I wanted async-native handling for pings and automatic Pydantic request validation out of the box, which keeps the API code clean and highly readable.
- **I chose APScheduler over Celery**: I wanted to avoid the complexity of setting up and maintaining separate broker (Redis) and worker containers. APScheduler allows me to run ping checks in a background thread inside the same API container.
- **I chose PostgreSQL over SQLite**: SQLite database files often lock during concurrent write operations and can throw permission errors when shared across Docker container volumes on Windows hosts. Postgres is standard and easily handles multi-container volume persistence.
- **I chose a Single-File Backend layout**: I merged routes, schemas, database connections, and the scheduler into `backend/main.py` (~150 lines) to eliminate directory-nesting overhead, making the codebase fast to audit, maintain, and package.

---

## 🤖 My AI-Driven Development Loop (Leveraging Coding Agents)

I leveraged **Cursor IDE (powered by Claude 3.5 Sonnet)** as my primary coding agent to accelerate development velocity, allowing me to build, test, and ship this full-stack MVP in less than an hour.

<table>
  <tr>
    <td valign="top" width="50%">

```mermaid
graph TD
    Stage0[1. Requirement Analysis] -->|I isolated parameters & blocked scope creep| Stage1[2. Architecture & Design]
    Stage1 -->|I compared tech stacks & designed schemas| Stage2[3. Scaffolding & Setup]
    Stage2 -->|I bypassed local script blocks with manual configs| Stage3[4. Backend API & Pinger]
    Stage3 -->|I built endpoints & integrated instant pings| Stage4[5. Frontend & Themes]
    Stage4 -->|I designed custom dark CSS and stats cards| Stage5[6. QA, Refactoring & Launch]
    Stage5 -->|I resolved 0ms JS bugs & configured Docker| Ready[MVP Fully Shipped 🚀]

    style Stage0 fill:#111827,stroke:#38bdf8,stroke-width:2px,color:#fff
    style Stage1 fill:#111827,stroke:#38bdf8,stroke-width:2px,color:#fff
    style Stage2 fill:#111827,stroke:#34d399,stroke-width:2px,color:#fff
    style Stage3 fill:#111827,stroke:#34d399,stroke-width:2px,color:#fff
    style Stage4 fill:#111827,stroke:#8b5cf6,stroke-width:2px,color:#fff
    style Stage5 fill:#111827,stroke:#ef4444,stroke-width:2px,color:#fff
    style Ready fill:#064e3b,stroke:#34d399,stroke-width:3px,color:#fff
```

</td>
<td valign="top" width="50%">
  <h4>How I Guided the Coding Agent:</h4>
  <ul>
    <li><strong>1. Requirements & Architecture</strong>: I prompted the agent to parse the specs, set PRD boundaries, and chose Postgres and APScheduler to limit container bloat.</li>
    <li><strong>2. Scaffolding & Setup</strong>: Bypassed Windows script locks by having the agent manually write package configs and HTML entry points.</li>
    <li><strong>3. Backend & Pinger</strong>: Generated FastAPI endpoints and independent background threads in a single main.py file.</li>
    <li><strong>4. Instant Pings</strong>: Moved the ping execution inside the POST request thread so the frontend renders UP/DOWN status instantly.</li>
    <li><strong>5. Frontend & Themes</strong>: Built React logic and styled it into a desaturated dark slate layout to align with dark theme standards.</li>
    <li><strong>6. QA & Launch</strong>: Inspected the code for edge case bugs (fixing 0ms truthy checks) and orchestrated compose with DB health checks.</li>
  </ul>
  <br/>
  <h4>Speed Boost Achieved:</h4>
  <p>Leveraging Cursor's inline editing and terminal commands eliminated hours of manual code wiring, environment script debugging, and hex-color selection adjustments, allowing me to ship in minutes.</p>
</td>
</tr>
</table>

### Why Cursor + Claude 3.5 Sonnet? (Trade-off Flow)

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

### AI Stack Comparison

| Tool / Model | Strengths | Weaknesses | Why I Chose It Over Others |
|---|---|---|---|
| **Cursor + Claude 3.5 Sonnet** <br>*(Chosen)* | • Direct folder/file context<br>• Inline multi-file code editing<br>• Terminal agent execution (Docker/npm) | • Higher latency than simple autocompletes | **I selected this** because the logical reasoning of Sonnet combined with Cursor's ability to run CLI commands allowed me to scaffold and debug the entire stack in minutes without leaving my editor. |
| **GitHub Copilot** | • Fast, inline line completions<br>• Low latency | • Cannot run shell commands<br>• Poor cross-file reasoning | **I rejected this** because it is too limited for scaffolding Docker files, database schemas, and wiring APIs together. |
| **ChatGPT / Claude Web** | • Good for generic syntax/Q&A | • High copy-paste friction<br>• Lacks local codebase context | **I rejected this** because copy-pasting code between the browser and my editor slows down development speed significantly. |

---

## 🌐 Production Cloud Topology (AWS)

```mermaid
graph LR
    Browser[User Browser] --> Route53[Route 53] --> ALB[Application Load Balancer]
    ALB -->|/*| S3[S3 Static Frontend]
    ALB -->|/api/*| ECS[ECS Fargate API Containers]
    ECS --> RDS[(RDS PostgreSQL DB)]
```

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
