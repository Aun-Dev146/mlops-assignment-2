"""
MLOps Inference API

FastAPI application for ML model prediction
- Loads trained model from models/model.pkl
- Provides /predict endpoint for inference
- Provides /health endpoint for health checks
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import joblib
import json
import os
import logging
from datetime import datetime
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MLOps Inference API",
    description="ML Model Inference API with health checks",
    version="1.0.0"
)

# Global variables for model and metadata
MODEL = None
MODEL_METADATA = None
MODEL_LOADED = False

# Pydantic models for request/response
class PredictionInput(BaseModel):
    """Input features for prediction"""
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    
    class Config:
        schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2
            }
        }

class PredictionOutput(BaseModel):
    """Output prediction response"""
    prediction: str
    confidence: float
    input_features: dict
    model_version: str
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_version: Optional[str]
    timestamp: str
    message: str

class ModelInfo(BaseModel):
    """Model information response"""
    model_name: str
    model_type: str
    features: List[str]
    classes: List[str]
    accuracy: float
    timestamp: str

# Startup event - Load model
@app.on_event("startup")
async def load_model():
    """Load trained model on startup"""
    global MODEL, MODEL_METADATA, MODEL_LOADED
    
    logger.info("=" * 50)
    logger.info("🚀 STARTING API SERVER")
    logger.info("=" * 50)
    
    try:
        # Try multiple possible paths for model
        possible_paths = [
            'models/model.pkl',
            './models/model.pkl',
            '/opt/airflow/models/model.pkl',
            '/app/models/model.pkl',
        ]
        
        model_path = None
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                break
        
        if not model_path:
            logger.error("❌ Model not found in any expected location!")
            MODEL_LOADED = False
            return
        
        # Load model
        logger.info(f"📂 Loading model from: {model_path}")
        MODEL = joblib.load(model_path)
        logger.info(f"✅ Model loaded successfully!")
        
        # Load metadata if available
        metadata_path = os.path.dirname(model_path) + '/metrics.json'
        if os.path.exists(metadata_path):
            logger.info(f"📄 Loading metadata from: {metadata_path}")
            with open(metadata_path, 'r') as f:
                MODEL_METADATA = json.load(f)
            logger.info(f"✅ Metadata loaded!")
            logger.info(f"   Features: {MODEL_METADATA.get('features_used', [])}")
            logger.info(f"   Classes: {MODEL_METADATA.get('classes', [])}")
            logger.info(f"   Train Accuracy: {MODEL_METADATA.get('train_accuracy', 0):.4f}")
        
        MODEL_LOADED = True
        logger.info("\n✅ API READY FOR PREDICTIONS!\n")
        
    except Exception as e:
        logger.error(f"❌ Error loading model: {str(e)}")
        MODEL_LOADED = False

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        HealthResponse: Current health status
    """
    logger.info("📋 Health check requested")
    
    if MODEL_LOADED and MODEL is not None:
        status = "healthy"
        message = "API is running and model is loaded"
        model_version = "1.0.0"
    else:
        status = "unhealthy"
        message = "API is running but model is not loaded"
        model_version = None
    
    return HealthResponse(
        status=status,
        model_loaded=MODEL_LOADED,
        model_version=model_version,
        timestamp=datetime.now().isoformat(),
        message=message
    )

# Model info endpoint
@app.get("/model-info", response_model=ModelInfo)
async def get_model_info():
    """
    Get model information
    
    Returns:
        ModelInfo: Details about the loaded model
    """
    logger.info("📊 Model info requested")
    
    if not MODEL_LOADED or MODEL is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    metadata = MODEL_METADATA or {}
    
    return ModelInfo(
        model_name="Random Forest Classifier",
        model_type="sklearn.ensemble.RandomForestClassifier",
        features=metadata.get('features_used', ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']),
        classes=metadata.get('classes', ['setosa', 'versicolor', 'virginica']),
        accuracy=metadata.get('train_accuracy', 1.0),
        timestamp=datetime.now().isoformat()
    )

# Prediction endpoint
@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """
    Make a prediction using the trained model
    
    Args:
        input_data: Input features (sepal_length, sepal_width, petal_length, petal_width)
    
    Returns:
        PredictionOutput: Prediction result with confidence
    """
    logger.info("🤖 Prediction requested")
    
    # Check if model is loaded
    if not MODEL_LOADED or MODEL is None:
        logger.error("❌ Model not loaded")
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please check server logs."
        )
    
    try:
        # Prepare input features
        features = np.array([[
            input_data.sepal_length,
            input_data.sepal_width,
            input_data.petal_length,
            input_data.petal_width
        ]])
        
        logger.info(f"📥 Input features: {features[0]}")
        
        # Make prediction
        prediction = MODEL.predict(features)[0]
        logger.info(f"🎯 Prediction: {prediction}")
        
        # Get confidence (probability of predicted class)
        prediction_proba = MODEL.predict_proba(features)[0]
        confidence = float(np.max(prediction_proba))
        logger.info(f"📈 Confidence: {confidence:.4f}")
        
        # Log successful prediction
        logger.info(f"✅ Prediction successful: {prediction} (confidence: {confidence:.4f})\n")
        
        return PredictionOutput(
            prediction=str(prediction),
            confidence=confidence,
            input_features={
                "sepal_length": input_data.sepal_length,
                "sepal_width": input_data.sepal_width,
                "petal_length": input_data.petal_length,
                "petal_width": input_data.petal_width
            },
            model_version="1.0.0",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Prediction failed: {str(e)}"
        )

# Batch prediction endpoint
@app.post("/predict-batch")
async def predict_batch(predictions: List[PredictionInput]):
    """
    Make multiple predictions at once
    
    Args:
        predictions: List of PredictionInput objects
    
    Returns:
        List of predictions
    """
    logger.info(f"🤖 Batch prediction requested for {len(predictions)} samples")
    
    if not MODEL_LOADED or MODEL is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded"
        )
    
    try:
        # Prepare batch features
        features = np.array([[
            p.sepal_length,
            p.sepal_width,
            p.petal_length,
            p.petal_width
        ] for p in predictions])
        
        # Make predictions
        batch_predictions = MODEL.predict(features)
        batch_probas = MODEL.predict_proba(features)
        
        results = []
        for i, (pred, proba) in enumerate(zip(batch_predictions, batch_probas)):
            results.append({
                "index": i,
                "prediction": str(pred),
                "confidence": float(np.max(proba)),
                "input_features": {
                    "sepal_length": predictions[i].sepal_length,
                    "sepal_width": predictions[i].sepal_width,
                    "petal_length": predictions[i].petal_length,
                    "petal_width": predictions[i].petal_width
                }
            })
        
        logger.info(f"✅ Batch prediction successful for {len(predictions)} samples\n")
        
        return {
            "total_samples": len(predictions),
            "predictions": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error during batch prediction: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Batch prediction failed: {str(e)}"
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "MLOps Inference API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "model_info": "/model-info",
            "predict": "/predict (POST)",
            "predict_batch": "/predict-batch (POST)",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "status": "running"
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"❌ Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting API server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
