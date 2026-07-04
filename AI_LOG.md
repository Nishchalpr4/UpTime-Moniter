# AI Collaboration Log

## AI Tech Stack

I used AI throughout the project as a development partner rather than a code generator.

**Tools Used**

* **Antigravity** – Primary development environment for planning, implementation, debugging, and refactoring.
* **ChatGPT** and Claude Chat – Used to discuss architecture, review implementation decisions, and improve documentation.

---

## Development Process

Instead of generating the entire application in one prompt, I built the project in small milestones.

1. Understand the assignment and define the MVP.
2. Design the project architecture.
3. Build the backend API.
4. Implement the background URL monitoring scheduler.
5. Build the React dashboard.
6. Connect the frontend and backend.
7. Dockerize the application.
8. Test the complete workflow.
9. Review and clean up the code before submission.

This iterative approach made it easier to validate each feature and fix issues early.

---

## Prompts

### Planning

> Read the assignment and help me identify the required features, recommended architecture, and anything that would be unnecessary for an MVP.

---

### Backend

> Build a clean FastAPI backend that allows adding URLs, periodically checks them, stores the latest status and response time, and exposes simple REST APIs. Keep the architecture minimal and explain your design decisions.

---

### Frontend

> Create a simple React dashboard that lists monitored URLs, their current status, latest response time, and automatically refreshes the data. Keep the UI clean and functional without unnecessary complexity.

---

### Docker

> Create Dockerfiles and a docker-compose.yml so the frontend and backend can be started with a single `docker compose up` command.

---

## Course Corrections

### 1. Simplifying the Architecture

The initial AI-generated solution introduced unnecessary abstraction for a small MVP. I refined the prompt to prioritize simplicity and removed components that were not required for the assignment.

---

### 2. Improving Error Handling

The initial implementation did not gracefully handle unreachable URLs and request timeouts. I updated the implementation so failed requests are recorded correctly and displayed as **DOWN** instead of causing application errors.

---

### 3. Frontend State Management

The first version of the dashboard refreshed inconsistently after adding a new URL. I refined the logic so new entries appear immediately and the dashboard stays synchronized with the backend.

---

## What I Learned

This project reinforced that AI is most effective when used iteratively. Breaking the work into smaller milestones, reviewing generated code, and refining prompts produced better results than trying to generate the entire application in a single step. Engineering judgment was still required to simplify the architecture, validate AI-generated code, and ensure the final solution met the assignment requirements.
