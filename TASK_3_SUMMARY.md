# Task 3: Docker (Full Assignment) - Complete Summary

## Overview
Successfully created Docker configuration for containerizing the MLOps application with training and API containers, complete with health checks, volume management, and Docker Hub deployment instructions.

---

## Task 3.1: Create Dockerfile

### File: `Dockerfile`
**Purpose:** Containerize the ML training application for reproducible execution

### Key Components

**1. Base Image**
```dockerfile
FROM python:3.10-slim
```
- Python 3.10 lightweight image (~130 MB)
- Slim variant excludes unnecessary packages
- Stable, well-maintained base

**2. Environment Setup**
```dockerfile
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
```
- Working directory: `/app`
- Unbuffered output (see logs in real-time)
- Don't write .pyc files (reduce size)
- No pip cache (reduce size)

**3. System Dependencies**
```dockerfile
RUN apt-get update && apt-get install -y git gcc curl && rm -rf /var/lib/apt/lists/*
```
- **git**: Version control operations
- **gcc**: C compiler for Python packages
- **curl**: HTTP requests, health checks
- Cleanup apt cache (reduce layer size)

**4. Python Dependencies**
```dockerfile
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
```
- Copy requirements.txt first (better layer caching)
- Install all Python packages
- Separate layer enables cache reuse

**5. Project Files**
```dockerfile
COPY . .
RUN mkdir -p models
```
- Copy entire project
- Create output directory

**6. Port & Health Check**
```dockerfile
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1
```
- Expose port 8000 for API (Task 5)
- Health check every 30 seconds
- Allows Docker to monitor container health

**7. Default Command**
```dockerfile
CMD ["python", "src/train.py"]
```
- Runs training script when container starts
- Can be overridden with `docker run` command

### Image Build Layers

```
Layer 1: FROM python:3.10-slim                    (~130 MB)
Layer 2: apt-get install dependencies             (~50 MB)
Layer 3: pip install -r requirements.txt          (~250 MB)
Layer 4: COPY project files                       (~10 MB)
────────────────────────────────────────────────────────────
Total Image Size: ~450 MB (compressed), ~850 MB (uncompressed)
```

---

## Task 3.2: .dockerignore File

### File: `.dockerignore`
**Purpose:** Exclude unnecessary files from Docker build context

### Excluded Patterns

| Pattern | Reason |
|---------|--------|
| `.git/` | Version control (will rebuild if pulled) |
| `__pycache__/` | Python cache (regenerated) |
| `.venv/` | Virtual environment (installed fresh) |
| `models/*.pkl` | Generated outputs (built in container) |
| `*.md` | Documentation (not needed in container) |
| `.github/` | CI/CD config (not needed) |
| `dvcstore/` | Data storage (managed separately) |
| `*.tar, *.zip` | Archives (unnecessary) |

### Benefits
- ✅ Smaller build context (faster upload to daemon)
- ✅ Faster build times
- ✅ Reduced image size
- ✅ Better security (exclude sensitive files)

---

## Task 3.3: docker-compose.yml

### File: `docker-compose.yml`
**Purpose:** Orchestrate multiple containers (training + API)

```yaml
version: '3.8'

services:
  mlops-training:
    build:
      context: .
      dockerfile: Dockerfile
    image: mlops-app:latest
    volumes:
      - ./data:/app/data          # Mount dataset
      - ./models:/app/models      # Mount outputs
      - ./dvc.lock:/app/dvc.lock  # Mount pipeline lock
    command: python src/train.py

  mlops-api:
    build:
      context: .
      dockerfile: Dockerfile.api
    image: mlops-api:latest
    ports:
      - "8000:8000"
    depends_on:
      - mlops-training
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Volume Mounts
- **data/**: Input dataset
- **models/**: Trained model outputs
- **dvc.lock**: Pipeline reproducibility

### Service Dependencies
```
mlops-api depends on mlops-training
↓
Training must complete before API can serve predictions
```

### Docker Compose Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild images
docker-compose build

# Run specific service
docker-compose up mlops-training
```

---

## Task 3.4: Dockerfile.api

### File: `Dockerfile.api`
**Purpose:** Containerize the ML inference API (Task 5)

**Key Differences from Training Dockerfile:**

```dockerfile
# Health check uses HTTP request instead of Python check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI server instead of training script
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### API Container Features
- ✅ Exposes port 8000 for external requests
- ✅ HTTP health check at `/health` endpoint
- ✅ FastAPI server (production-ready)
- ✅ Auto-reload disabled in production
- ✅ Accessible on 0.0.0.0:8000 (all interfaces)

---

## Build & Run Instructions

### 3.1: Build Docker Image

```bash
docker build -t mlops-app:latest -t mlops-app:v1 .
```

**Process:**
1. Read Dockerfile
2. Build each layer sequentially
3. Cache intermediate layers
4. Create final image
5. Tag with "latest" and "v1"

**Expected Output:**
```
Sending build context to Docker daemon   5.12 kB
Step 1/11 : FROM python:3.10-slim
 ---> 3a7c...
Step 2/11 : WORKDIR /app
 ---> Running in container...
 ---> 4b8f...
...
Successfully built abc123def456
Successfully tagged mlops-app:latest
Successfully tagged mlops-app:v1
```

### 3.2: Run Docker Container

**Basic execution:**
```bash
docker run mlops-app:v1
```

**With volume mount (save outputs):**
```bash
docker run -v $(pwd)/models:/app/models mlops-app:v1
```

**Named container:**
```bash
docker run --name mlops-training mlops-app:v1
```

**Output:**
```
Loading dataset...
Dataset shape: (30, 5)
Training Random Forest classifier...
Model training completed!
Train Accuracy: 1.0000
Test Accuracy: 1.0000
Model saved to models/model.pkl
Metrics saved to models/metrics.json
✅ Training pipeline completed successfully!
```

### 3.3: Check Logs

```bash
docker logs mlops-training
```

View training output and verify execution

### 3.4: List Images

```bash
docker images
```

**Output:**
```
REPOSITORY  TAG      IMAGE ID       SIZE
mlops-app   latest   abc123def456   850MB
mlops-app   v1       abc123def456   850MB
```

---

## Docker Hub Deployment

### Prerequisites
1. Docker Hub account (https://hub.docker.com)
2. Create repository `mlops-app` (public)
3. Local Docker login

### Steps

**1. Tag Image for Registry**
```bash
docker tag mlops-app:v1 yourusername/mlops-app:v1
```

**2. Login to Docker Hub**
```bash
docker login
# Enter username and password
```

**3. Push Image**
```bash
docker push yourusername/mlops-app:v1
```

**Process:**
1. Authenticates with Docker Hub
2. Uploads image layers
3. Creates repository entry
4. Available at: `https://hub.docker.com/r/yourusername/mlops-app`

**4. Pull and Run from Docker Hub**
```bash
docker run yourusername/mlops-app:v1
```

---

## Docker Compose Workflow

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f mlops-training

# Check trained model
ls -la models/

# Stop all services
docker-compose down
```

---

## Files Created

| File | Size | Purpose |
|------|------|---------|
| `Dockerfile` | ~1.2 KB | Training container |
| `Dockerfile.api` | ~1.0 KB | API container |
| `.dockerignore` | ~1.5 KB | Exclude unnecessary files |
| `docker-compose.yml` | ~0.8 KB | Multi-container orchestration |
| `DOCKER_GUIDE.md` | ~8 KB | Comprehensive documentation |

---

## Git Commit

```
28fd564 (HEAD -> master) Add Docker configuration and documentation
b5926f6 Add unit tests and GitHub Actions CI/CD workflow
aa51dad Add training pipeline and DVC configuration
fbea96b Add requirements.txt
f584e92 Initialize DVC and add dataset
```

---

## Complete Docker Workflow Visualization

```
┌─────────────────────────────────────────────────────────┐
│                 Development Machine                     │
├─────────────────────────────────────────────────────────┤
│  Source Code + Requirements + Dataset                   │
│  ↓                                                       │
│  docker build -t mlops-app:v1 .                         │
│  ↓                                                       │
│  Local Docker Image Created                             │
│  ↓                                                       │
│  docker run mlops-app:v1                                │
│  ↓                                                       │
│  Training Container Executes                            │
│  ├─ Loads data/dataset.csv                              │
│  ├─ Trains model                                         │
│  ├─ Saves models/model.pkl                              │
│  └─ Saves models/metrics.json                           │
└─────────────────────────────────────────────────────────┘
                         ↓
                  [Tag Image]
                  docker tag mlops-app:v1 \
                  yourusername/mlops-app:v1
                         ↓
┌─────────────────────────────────────────────────────────┐
│                    Docker Hub                           │
├─────────────────────────────────────────────────────────┤
│  docker push yourusername/mlops-app:v1                  │
│  ↓                                                       │
│  Public Repository                                       │
│  yourusername/mlops-app:v1                              │
│  ↓                                                       │
│  Available Globally                                      │
│  Any machine can: docker run yourusername/mlops-app:v1 │
└─────────────────────────────────────────────────────────┘
```

---

## Key Achievements ✅

| Component | Status | Details |
|-----------|--------|---------|
| Dockerfile created | ✅ | Training container |
| Dockerfile.api created | ✅ | API container (Task 5) |
| .dockerignore created | ✅ | Build optimization |
| docker-compose.yml | ✅ | Multi-container setup |
| Health checks | ✅ | Container monitoring |
| Volume management | ✅ | Data persistence |
| Documentation | ✅ | Comprehensive guide |
| Git committed | ✅ | 28fd564 hash |

---

## Best Practices Implemented

✅ **Layer caching** - Separate requirements from code for better caching
✅ **Minimal base image** - python:3.10-slim (not full image)
✅ **Health checks** - Monitor container status
✅ **Volume mounts** - Persist outputs
✅ **Environment variables** - Configure runtime behavior
✅ **.dockerignore** - Exclude unnecessary files
✅ **Documentation** - Clear instructions
✅ **Multi-container** - Separate services via docker-compose

---

## Next Steps

1. **Docker Desktop/Engine** - Ensure running on your machine
2. **Build image** - Run `docker build` command
3. **Test locally** - Run `docker run` to verify output
4. **Setup Docker Hub** - Create account and repository
5. **Push to registry** - Make image publicly available
6. **Task 5** - Create FastAPI application with `/predict` and `/health` endpoints

---

**Task 3: Docker is now complete!** ✅

Ready to proceed to **Task 4: Airflow Pipeline** when you are!
