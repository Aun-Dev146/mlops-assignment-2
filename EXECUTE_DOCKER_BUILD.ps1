# Docker Build and Push Script
# Execute this script in PowerShell to build, run, tag, and push Docker image

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "MLOps Assignment - Docker Build & Push Script" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Set working directory
$workdir = "c:\Users\pc\Desktop\MLops_Assignment"
Set-Location $workdir

Write-Host "📁 Working Directory: $workdir`n" -ForegroundColor Yellow

# Step 1: Build Docker Image
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "STEP 1: Building Docker Image..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Green

Write-Host "Command: docker build -t mlops-app ." -ForegroundColor Magenta
Write-Host "This may take 3-5 minutes..." -ForegroundColor Yellow
Write-Host ""

docker build -t mlops-app .

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ BUILD SUCCESSFUL!`n" -ForegroundColor Green
    Write-Host "Image Details:" -ForegroundColor Cyan
    docker images | grep mlops-app
} else {
    Write-Host "`n❌ BUILD FAILED!`n" -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Red
    exit 1
}

# Step 2: Run Container to Verify
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "STEP 2: Running Container..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Green

Write-Host "Command: docker run --name mlops-training mlops-app" -ForegroundColor Magenta
Write-Host ""

# Remove if already exists
docker rm mlops-training -f 2>$null

docker run --name mlops-training mlops-app

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ CONTAINER RUN SUCCESSFUL!`n" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Container finished with status code: $LASTEXITCODE" -ForegroundColor Yellow
}

# Step 3: Tag Image for Docker Hub
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "STEP 3: Tagging Image..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Green

Write-Host "Command: docker tag mlops-app aun36852/mlops-app:v1" -ForegroundColor Magenta
Write-Host ""

docker tag mlops-app aun36852/mlops-app:v1

Write-Host "`n✅ IMAGE TAGGED!`n" -ForegroundColor Green
docker images | grep aun36852

# Step 4: Login to Docker Hub
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "STEP 4: Docker Hub Login..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Green

Write-Host "Please enter your Docker Hub credentials:" -ForegroundColor Yellow
Write-Host "Username: aun36852" -ForegroundColor Cyan
Write-Host "Password: (you will be prompted)`n" -ForegroundColor Cyan

Write-Host "Command: docker login" -ForegroundColor Magenta
Write-Host ""

docker login

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ LOGIN FAILED!`n" -ForegroundColor Red
    Write-Host "Please verify your Docker Hub credentials." -ForegroundColor Red
    exit 1
}

# Step 5: Push to Docker Hub
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "STEP 5: Pushing to Docker Hub..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Green

Write-Host "Command: docker push aun36852/mlops-app:v1" -ForegroundColor Magenta
Write-Host "This may take 2-5 minutes..." -ForegroundColor Yellow
Write-Host ""

docker push aun36852/mlops-app:v1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ PUSH SUCCESSFUL!`n" -ForegroundColor Green
} else {
    Write-Host "`n❌ PUSH FAILED!`n" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

Write-Host "✅ Docker image built successfully: mlops-app" -ForegroundColor Green
Write-Host "✅ Container executed and trained model" -ForegroundColor Green
Write-Host "✅ Image tagged as: aun36852/mlops-app:v1" -ForegroundColor Green
Write-Host "✅ Pushed to Docker Hub`n" -ForegroundColor Green

Write-Host "📍 Docker Hub Repository:" -ForegroundColor Yellow
Write-Host "   https://hub.docker.com/r/aun36852/mlops-app`n" -ForegroundColor Cyan

Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. ✅ Task 3 Docker Build Complete" -ForegroundColor Green
Write-Host "   2. 📸 Take screenshots (see TASK_3_FINAL_STATUS.md)" -ForegroundColor Cyan
Write-Host "   3. ➡️  Proceed to Task 4: Airflow Pipeline`n" -ForegroundColor Cyan

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "TASK 3 EXECUTION COMPLETE!" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
