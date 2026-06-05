# GS Inima Weather API Challenge 🌍❄️

A full-stack web application designed to retrieve, process, and visualize meteorological data from the Antarctic station **Gabriel de Castilla**.

---

## 🚀 Quick Start

This project is fully containerized to ensure reproducibility across any environment without dependency conflicts.

### Prerequisites

- Docker
- Docker Compose

### Installation

Clone the repository and start the infrastructure:

```bash
git clone https://github.com/roberto-garcia-ramirez/gsinima-weather-api-challenge.git
cd gsinima-weather-api-challenge
docker-compose up --build
```

### Access the Application

| Service | URL |
|----------|-----|
| Frontend Dashboard | http://localhost:5173 |
| Backend API Documentation (Swagger) | http://localhost:8000/docs |

---

## 🏗️ Architecture & Technical Decisions

This project was designed following production-oriented principles while keeping the setup lightweight and easy to evaluate.

### 1. Resilient Architecture: API Fallback (Mocking System)

**Decision:** Implemented an automatic data mocking system in the backend.

**Rationale:**  
Third-party providers such as AEMET can experience downtime, rate limits, or delayed credential provisioning. To prevent the application from becoming unavailable, the backend automatically detects the absence of a valid `AEMET_API_KEY`.

When no API key is present, the application transparently falls back to a locally generated dataset, ensuring:

- High availability
- Uninterrupted frontend development
- Consistent evaluation of business logic
- Reliable database and visualization testing

---

### 2. Database: Asynchronous SQLite (`aiosqlite`)

**Decision:** Used SQLite with SQLAlchemy's asynchronous engine.

**Rationale:**  
SQLite provides a zero-configuration database solution ideal for technical challenges and local development environments.

To preserve FastAPI's asynchronous request handling, the project leverages `aiosqlite`, allowing the entire request lifecycle to remain non-blocking.

This architecture also enables a straightforward migration to PostgreSQL or another relational database by simply updating the connection string and database configuration.

---

### 3. Containerization (Docker)

**Decision:** Multi-container architecture using Docker Compose.

**Rationale:**  
Containerization eliminates environment inconsistencies and the classic *"it works on my machine"* problem.

Benefits include:

- Reproducible development environments
- Simplified setup process
- Isolated frontend and backend services
- Single-command project startup

```bash
docker-compose up --build
```

---

### 4. Continuous Integration (CI)

**Decision:** Configured a GitHub Actions workflow.

**Rationale:**  
To maintain code quality and prevent regressions, every push to the `main` branch automatically triggers:

1. Test database initialization
2. Dependency installation
3. Execution of the complete `pytest` suite

This workflow ensures that new changes do not break existing functionality and reflects modern DevOps best practices.

---

## 🛠️ Tech Stack

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy (Async)
- Pydantic
- Pytest

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Recharts

### DevOps

- Docker
- Docker Compose
- GitHub Actions

---

## 📂 Repository

GitHub Repository:

https://github.com/roberto-garcia-ramirez/gsinima-weather-api-challenge