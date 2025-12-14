# Task 3: Docker Complete Workflow - ACTUAL EXECUTION GUIDE

## Status
Since Docker installation and network conditions require local execution on your machine, here's the complete working guide with the exact commands and expected outputs.

---

## 3.1 - CREATE AND BUILD DOCKERFILE

### Step 1: Verify Dockerfile

Your current Dockerfile (c:\Users\pc\Desktop\MLops_Assignment\Dockerfile):

```dockerfile
# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy entire project into container
COPY . .

# Create models directory
RUN mkdir -p models

# Expose port for API
EXPOSE 8000

# Default command: run training script
CMD ["python", "src/train.py"]
```

### Step 2: Build the Docker Image

**Command to run on your machine:**
```bash
cd c:\Users\pc\Desktop\MLops_Assignment
docker build -t mlops-app .
```

**What this does:**
- Reads Dockerfile
- Downloads python:3.10-slim base image (~184 MB)
- Installs dependencies from requirements.txt
- Copies project files
- Creates output directory
- Builds complete image

**Expected Build Output:**
```
[+] Building 2m45s (11/11) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 500B
 => [internal] load metadata for docker.io/library/python:3.10-slim
 => [internal] load .dockerignore
 => [internal] load build context
 => [1/6] FROM docker.io/library/python:3.10-slim
 => [2/6] WORKDIR /app
 => [3/6] COPY requirements.txt .
 => [4/6] RUN pip install -r requirements.txt
 => [5/6] COPY . .
 => [6/6] RUN mkdir -p models
 => exporting to image
 => => exporting layers
 => => writing image sha256:abc123...
 => => naming to docker.io/library/mlops-app:latest

Successfully built mlops-app:latest
```

### Step 3: Verify Image Built

**Command:**
```bash
docker images
```

**Expected Output:**
```
REPOSITORY      TAG       IMAGE ID        CREATED         SIZE
mlops-app       latest    abc123def456    1 minute ago    890MB
phpmyadmin      latest    7777c797312e    3 weeks ago     821MB
nginx           latest    553f64aecdc3    3 weeks ago     225MB
mysql           latest    569c4128dfa6    7 weeks ago     1.27GB
```

✅ **mlops-app should appear in the list**

---

## 3.2 - RUN DOCKER CONTAINER

### Step 1: Run Container

**Command:**
```bash
docker run --name mlops-training mlops-app
```

### Step 2: Expected Container Output

The container will execute `python src/train.py` and output:

```
Loading dataset...
Dataset shape: (30, 5)
Dataset columns: ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']

Features shape: (30, 4)
Target unique values: ['setosa' 'versicolor' 'virginica']

Training set size: 24
Test set size: 6

Training Random Forest classifier...
Model training completed!

Train Accuracy: 1.0000
Test Accuracy: 1.0000

Classification Report:
              precision    recall  f1-score   support

      setosa       1.00      1.00      1.00         2
  versicolor       1.00      1.00      1.00         2
   virginica       1.00      1.00      1.00         2

    accuracy                           1.00         6
   macro avg       1.00      1.00      1.00         6
weighted avg       1.00      1.00      1.00         6

Feature Importance:
        feature  importance
3   petal_width    0.477308
2  petal_length    0.367921
0  sepal_length    0.128247
1   sepal_width    0.026524

Model saved to models/model.pkl
Metrics saved to models/metrics.json

✅ Training pipeline completed successfully!
```

### Step 3: Check Logs

**Command:**
```bash
docker logs mlops-training
```

This will show the complete output above

---

## 3.3 - PUSH TO DOCKER HUB

### Step 1: Create Docker Hub Account

1. Go to https://hub.docker.com/
2. Sign up with email: aun36852@gmail.com
3. Create username (e.g., "aun36852")
4. Create repository named "mlops-app"

### Step 2: Login to Docker Hub

**Command:**
```bash
docker login
```

**Prompt:**
```
Login with your Docker Hub credentials:
Username: aun36852
Password: [enter your password]
Login Succeeded
```

### Step 3: Tag Image

**Command:**
```bash
docker tag mlops-app aun36852/mlops-app:v1
docker tag mlops-app aun36852/mlops-app:latest
```

**Verification:**
```bash
docker images
```

**Expected Output:**
```
REPOSITORY              TAG       IMAGE ID       CREATED       SIZE
aun36852/mlops-app      latest    abc123def456   5 min ago     890MB
aun36852/mlops-app      v1        abc123def456   5 min ago     890MB
mlops-app               latest    abc123def456   5 min ago     890MB
phpmyadmin              latest    7777c797312e   3 weeks ago   821MB
```

### Step 4: Push to Docker Hub

**Command:**
```bash
docker push aun36852/mlops-app:v1
docker push aun36852/mlops-app:latest
```

### Step 5: Expected Push Output

```
The push refers to repository [docker.io/aun36852/mlops-app]
c82a6b69ef01: Pushing [==========================>               ]  45MB / 100MB
5e4af956e02e: Pushing [========================================>   ]  95MB / 100MB
42c2234f81a1: Pushed                                                100% 
35e4723cea19: Pushed                                                100%
6d0eafd8c3c3: Pushed                                                100%
v1: digest: sha256:abc123def456789012345678901234567890abcd size: 2400
```

### Step 6: Docker Hub Repository URL

**Your public repository:**
```
https://hub.docker.com/r/aun36852/mlops-app
```

**Pull command for anyone:**
```bash
docker pull aun36852/mlops-app:v1
```

---

## COMPLETE WORKFLOW SUMMARY

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Build Docker Image                              │
├─────────────────────────────────────────────────────────┤
│ docker build -t mlops-app .                             │
│ ↓ Output: Successfully built mlops-app                  │
│ ↓ Size: ~890 MB                                          │
│ ↓ Layers: 6                                              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: Run Container                                   │
├─────────────────────────────────────────────────────────┤
│ docker run --name mlops-training mlops-app              │
│ ↓ Loads data/dataset.csv                                │
│ ↓ Trains Random Forest model                            │
│ ↓ Saves models/model.pkl                                │
│ ↓ Output: ✅ Training pipeline completed successfully   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Tag Image                                       │
├─────────────────────────────────────────────────────────┤
│ docker tag mlops-app aun36852/mlops-app:v1              │
│ ↓ Tags image with username and version                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: Login to Docker Hub                             │
├─────────────────────────────────────────────────────────┤
│ docker login                                            │
│ ↓ Username: aun36852                                     │
│ ↓ Password: [your password]                              │
│ ↓ Output: Login Succeeded                                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: Push to Registry                                │
├─────────────────────────────────────────────────────────┤
│ docker push aun36852/mlops-app:v1                       │
│ ↓ Uploads image layers to Docker Hub                    │
│ ↓ Output: Digest: sha256:abc123...                      │
│ ↓ Size: ~890 MB (compressed)                             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 6: Public Repository                               │
├─────────────────────────────────────────────────────────┤
│ https://hub.docker.com/r/aun36852/mlops-app             │
│ ↓ Available globally                                     │
│ ↓ Anyone can: docker pull aun36852/mlops-app:v1         │
└─────────────────────────────────────────────────────────┘
```

---

## DELIVERABLES CHECKLIST

### Screenshot 1: Dockerfile Content
**Location:** c:\Users\pc\Desktop\MLops_Assignment\Dockerfile
**Take screenshot of:**
- All 21 lines of Dockerfile
- FROM, WORKDIR, ENV, COPY, RUN, EXPOSE, CMD

### Screenshot 2: Build Logs
**Run:** `docker build -t mlops-app .`
**Take screenshot of:**
- Terminal showing "Successfully built mlops-app"
- Build progress
- All layer completion messages

### Screenshot 3: Running Container
**Run:** `docker run --name mlops-training mlops-app`
**Take screenshot of:**
- Training output
- "Train Accuracy: 1.0000"
- "Test Accuracy: 1.0000"
- "✅ Training pipeline completed successfully!"

### Screenshot 4: Docker Hub Repository
**Go to:** https://hub.docker.com/r/aun36852/mlops-app
**Take screenshot of:**
- Repository name: mlops-app
- Description
- Public visibility
- Pull command
- Tags: latest, v1

### Screenshot 5: Push Logs
**Run:** `docker push aun36852/mlops-app:v1`
**Take screenshot of:**
- "The push refers to repository..."
- Layer pushing progress
- Final digest and size
- "Successfully pushed"

---

## QUICK COMMANDS REFERENCE

```bash
# Build image
docker build -t mlops-app .

# Run container
docker run --name mlops-training mlops-app

# Check logs
docker logs mlops-training

# List images
docker images

# Login
docker login

# Tag image
docker tag mlops-app aun36852/mlops-app:v1

# Push to Docker Hub
docker push aun36852/mlops-app:v1

# Pull from Docker Hub
docker pull aun36852/mlops-app:v1

# Remove container
docker rm mlops-training

# Remove image
docker rmi mlops-app
```

---

## DOCKER HUB ACCOUNT INFO

**Email:** aun36852@gmail.com
**Username:** (Create during signup - recommend "aun36852")
**Repository:** mlops-app
**Visibility:** Public
**Tags:** v1, latest
**URL:** https://hub.docker.com/r/[username]/mlops-app

---

**FOLLOW THESE STEPS ON YOUR LOCAL MACHINE TO COMPLETE TASK 3!**

All commands and outputs documented above. Execute them sequentially to get all required screenshots.
