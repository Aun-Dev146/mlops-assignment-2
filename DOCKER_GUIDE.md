# Task 3: Docker Documentation

## Overview
This document explains the Docker setup for the MLOps project, including how to build, run, and push the Docker image to Docker Hub.

---

## Task 3.1: Create Dockerfile

### File: `Dockerfile`

**Purpose:** Containerize the ML training application

```dockerfile
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y \
    git \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .
RUN mkdir -p models

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

CMD ["python", "src/train.py"]
```

### Dockerfile Components Explained

| Component | Purpose |
|-----------|---------|
| **FROM python:3.10-slim** | Base image: Python 3.10 with minimal size |
| **WORKDIR /app** | Set working directory inside container |
| **ENV variables** | Configure Python behavior (unbuffered, no cache) |
| **apt-get update** | Install system dependencies (git, gcc, curl) |
| **COPY requirements.txt** | Copy dependencies list first (better caching) |
| **pip install** | Install Python packages from requirements.txt |
| **COPY . .** | Copy entire project into container |
| **mkdir -p models** | Create output directory |
| **EXPOSE 8000** | Expose port for API (Task 5) |
| **HEALTHCHECK** | Docker health check (every 30s) |
| **CMD** | Default command when container starts |

### Build Optimization

**Layer Caching Strategy:**
1. Base image (cached)
2. System dependencies (cached)
3. requirements.txt (cached separately from code)
4. Code changes (invalidates cache only for subsequent layers)

This ensures Docker reuses cached layers and only rebuilds when code changes.

---

## Task 3.2: .dockerignore File

### File: `.dockerignore`

**Purpose:** Exclude unnecessary files from Docker build context

**Excluded Items:**
- `.git/` - Version control
- `__pycache__/` - Python cache
- `.venv/` - Virtual environment
- `.github/` - GitHub Actions files
- `*.md` - Documentation
- `models/*.pkl` - Will be generated in container
- Large files and archives

**Benefits:**
- Smaller build context
- Faster build times
- Reduced image size

---

## Commands

### 3.1: Build Docker Image

```bash
docker build -t mlops-app:latest -t mlops-app:v1 .
```

**Breakdown:**
- `docker build` - Build an image from Dockerfile
- `-t mlops-app:latest` - Tag with "latest" (latest version)
- `-t mlops-app:v1` - Tag with "v1" (version 1)
- `.` - Use Dockerfile in current directory

**Output:**
```
Sending build context to Docker daemon  ...
Step 1/11 : FROM python:3.10-slim
 ---> [image_hash]
Step 2/11 : WORKDIR /app
 ---> Using cache
 ---> [image_hash]
...
Step 11/11 : CMD ["python", "src/train.py"]
 ---> [image_hash]
Successfully built [image_hash]
Successfully tagged mlops-app:latest
Successfully tagged mlops-app:v1
```

---

### 3.2: Run Docker Container

```bash
docker run mlops-app:latest
```

**With output logging:**
```bash
docker run --name mlops-training mlops-app:v1
```

**With volume mounts (for outputs):**
```bash
docker run -v $(pwd)/models:/app/models mlops-app:latest
```

**Command Explanation:**
- `docker run` - Create and run new container
- `-v $(pwd)/models:/app/models` - Mount local models folder to container
- `--name mlops-training` - Give container a name

**Container Execution:**
1. Pulls image if not local
2. Creates new container
3. Mounts volumes
4. Runs `python src/train.py`
5. Exits when training completes

---

### 3.3: List Docker Images

```bash
docker images
```

**Output:**
```
REPOSITORY     TAG      IMAGE ID      CREATED      SIZE
mlops-app      latest   abc123def456  2 hours ago  850MB
mlops-app      v1       abc123def456  2 hours ago  850MB
python         3.10-slim xyz789...    1 week ago   130MB
```

---

### 3.4: Check Container Logs

```bash
docker logs mlops-training
```

**Output shows:**
- Dataset loading progress
- Training output
- Accuracy metrics
- Model saving confirmation

---

### 3.5: Tag Image for Docker Hub

```bash
docker tag mlops-app:v1 yourusername/mlops-app:v1
```

**Components:**
- `yourusername` - Your Docker Hub username
- `mlops-app` - Repository name
- `v1` - Version tag

---

### 3.6: Push to Docker Hub

**Prerequisites:**
1. Create Docker Hub account (https://hub.docker.com)
2. Create repository (mlops-app)
3. Login locally: `docker login`

**Push command:**
```bash
docker push yourusername/mlops-app:v1
```

**Process:**
1. Authenticates with Docker Hub
2. Uploads image layers
3. Creates repository if needed
4. Tags version in registry

**Public URL:**
```
https://hub.docker.com/r/yourusername/mlops-app
```

---

## Docker Image Details

### Image Size
- **Base Python 3.10-slim:** ~130 MB
- **System packages:** ~50 MB
- **Python packages:** ~200 MB
- **Project files:** ~10 MB
- **Total:** ~400-500 MB (compressed: ~850 MB when pulled)

### Image Contents
```
/app/
├── src/
│   └── train.py          # Training script
├── data/
│   └── dataset.csv       # Dataset (via volume mount)
├── models/               # Output directory
├── tests/
│   └── test_train.py    # Unit tests
├── .dvc/                 # DVC configuration
├── requirements.txt      # Python packages
├── Dockerfile           # Build instructions
├── dvc.yaml            # Pipeline config
└── dvc.lock            # Pipeline lock file
```

---

## Docker Compose Setup

### File: `docker-compose.yml`

**Purpose:** Orchestrate multiple containers

```yaml
version: '3.8'

services:
  mlops-training:
    build:
      context: .
      dockerfile: Dockerfile
    image: mlops-app:latest
    container_name: mlops-training-container
    volumes:
      - ./data:/app/data
      - ./models:/app/models
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
```

### Docker Compose Commands

**Start all services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Stop all services:**
```bash
docker-compose down
```

---

## Workflow: Build → Run → Push

```
1. Build Image
   docker build -t mlops-app:v1 .
        ↓
2. Run Container
   docker run mlops-app:v1
        ↓
3. Verify Output
   docker logs [container_id]
        ↓
4. Tag for Registry
   docker tag mlops-app:v1 username/mlops-app:v1
        ↓
5. Push to Docker Hub
   docker push username/mlops-app:v1
        ↓
6. Public Repository
   https://hub.docker.com/r/username/mlops-app
```

---

## Best Practices

✅ **Use slim base images** - Reduces size and attack surface
✅ **Layer caching** - Put least-changed items last
✅ **Multi-stage builds** - Can optimize further (advanced)
✅ **Health checks** - Monitor container status
✅ **Environment variables** - Configure runtime behavior
✅ **Volume mounts** - Separate data from containers
✅ **Tagging strategy** - Use semantic versioning (v1, v1.0, latest)
✅ **Documented steps** - Clear build and run instructions

---

## Troubleshooting

### Docker daemon not running
**Solution:** Start Docker Desktop on Windows/Mac or Docker service on Linux

### Image build fails
**Solution:** Check:
- Python version compatibility
- Requirements.txt syntax
- Dockerfile syntax
- System package availability

### Container exits immediately
**Solution:** Check logs
```bash
docker logs [container_name]
```

### Permission denied when pushing
**Solution:** Login to Docker Hub
```bash
docker login
```

---

## Security Considerations

1. **Scan for vulnerabilities:**
   ```bash
   docker scan mlops-app:v1
   ```

2. **Use official base images** - More secure than random images

3. **Don't commit secrets** - Use environment variables or secrets management

4. **Minimize layers** - Reduces attack surface

5. **Regular updates** - Keep base image and packages updated

---

## Next Steps

1. **Install Docker** - If not already installed
2. **Build image** - Run `docker build` command
3. **Test locally** - Run `docker run` to verify
4. **Setup Docker Hub** - Create account and repository
5. **Push image** - Make it available globally
6. **Task 5** - Create API container (Dockerfile.api)

---

**Task 3: Docker is now documented and ready!** ✅
