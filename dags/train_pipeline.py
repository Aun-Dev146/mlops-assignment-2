"""
MLOps Training Pipeline DAG

This DAG orchestrates the complete ML training pipeline:
1. Load data
2. Train model
3. Save trained model
4. Log results
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'mlops',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'train_pipeline',
    default_args=default_args,
    description='MLOps Training Pipeline',
    schedule_interval='@daily',
    catchup=False,
    tags=['mlops', 'training'],
)

# Python functions for tasks
def load_data(**context):
    """Load training data from CSV"""
    logger.info("=" * 50)
    logger.info("📁 TASK 1: LOADING DATA")
    logger.info("=" * 50)
    
    try:
        # Try multiple possible paths
        possible_paths = [
            '/opt/airflow/data/dataset.csv',
            './data/dataset.csv',
            '/data/dataset.csv',
            '../data/dataset.csv',
        ]
        
        data_path = None
        for path in possible_paths:
            if os.path.exists(path):
                data_path = path
                break
        
        if not data_path:
            logger.error("Dataset not found in any expected location!")
            raise FileNotFoundError("dataset.csv not found")
        
        logger.info(f"✓ Found dataset at: {data_path}")
        
        df = pd.read_csv(data_path)
        logger.info(f"✓ Dataset loaded successfully")
        logger.info(f"✓ Shape: {df.shape}")
        logger.info(f"✓ Columns: {list(df.columns)}")
        logger.info(f"✓ Missing values: {df.isnull().sum().sum()}")
        
        # Save to XCom for next tasks
        context['task_instance'].xcom_push(key='dataset', value=df.to_json())
        
        logger.info("✓ Data loading completed successfully!\n")
        return {'status': 'success', 'shape': df.shape}
        
    except Exception as e:
        logger.error(f"✗ Error loading data: {str(e)}")
        raise

def train_model(**context):
    """Train the ML model"""
    logger.info("=" * 50)
    logger.info("🤖 TASK 2: TRAINING MODEL")
    logger.info("=" * 50)
    
    try:
        # Get data from XCom
        ti = context['task_instance']
        data_json = ti.xcom_pull(task_ids='load_data', key='dataset')
        df = pd.read_json(data_json)
        
        logger.info(f"✓ Received dataset: {df.shape}")
        
        # Prepare features and target
        X = df.drop('species', axis=1)
        y = df['species']
        
        logger.info(f"✓ Features: {list(X.columns)}")
        logger.info(f"✓ Target classes: {list(y.unique())}")
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"✓ Train set size: {len(X_train)}")
        logger.info(f"✓ Test set size: {len(X_test)}")
        
        # Train Random Forest model
        logger.info("✓ Training Random Forest Classifier (100 trees)...")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        logger.info("✓ Model training completed!")
        
        # Evaluate model
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        train_accuracy = accuracy_score(y_train, y_pred_train)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        
        logger.info(f"\n📊 MODEL PERFORMANCE:")
        logger.info(f"   Train Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
        logger.info(f"   Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
        
        # Feature importance
        feature_importance = dict(zip(X.columns, model.feature_importances_))
        logger.info(f"\n📈 FEATURE IMPORTANCE:")
        for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {feature}: {importance:.4f}")
        
        # Save model metrics to XCom
        metrics = {
            'train_accuracy': float(train_accuracy),
            'test_accuracy': float(test_accuracy),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'features_used': list(X.columns),
            'classes': list(y.unique()),
            'feature_importance': feature_importance
        }
        ti.xcom_push(key='metrics', value=json.dumps(metrics))
        ti.xcom_push(key='model', value=joblib.dumps(model))
        
        logger.info("\n✓ Model training completed successfully!\n")
        return {'status': 'success', 'train_accuracy': train_accuracy, 'test_accuracy': test_accuracy}
        
    except Exception as e:
        logger.error(f"✗ Error training model: {str(e)}")
        raise

def save_model(**context):
    """Save trained model to disk"""
    logger.info("=" * 50)
    logger.info("💾 TASK 3: SAVING MODEL")
    logger.info("=" * 50)
    
    try:
        # Create models directory if it doesn't exist
        model_dir = '/opt/airflow/models'
        os.makedirs(model_dir, exist_ok=True)
        logger.info(f"✓ Model directory: {model_dir}")
        
        # Get model from XCom
        ti = context['task_instance']
        model_bytes = ti.xcom_pull(task_ids='train_model', key='model')
        model = joblib.loads(model_bytes)
        
        metrics_json = ti.xcom_pull(task_ids='train_model', key='metrics')
        metrics = json.loads(metrics_json)
        
        # Save model
        model_path = os.path.join(model_dir, 'model.pkl')
        joblib.dump(model, model_path)
        logger.info(f"✓ Model saved to: {model_path}")
        
        # Get file size
        model_size = os.path.getsize(model_path)
        logger.info(f"✓ Model file size: {model_size / 1024:.2f} KB")
        
        # Save metrics
        metrics_path = os.path.join(model_dir, 'metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"✓ Metrics saved to: {metrics_path}")
        
        # Log metrics summary
        logger.info(f"\n📋 SAVED METRICS:")
        logger.info(f"   Train Accuracy: {metrics['train_accuracy']:.4f}")
        logger.info(f"   Test Accuracy: {metrics['test_accuracy']:.4f}")
        logger.info(f"   Model type: Random Forest Classifier")
        logger.info(f"   Features: {len(metrics['features_used'])}")
        logger.info(f"   Classes: {len(metrics['classes'])}")
        
        logger.info("\n✓ Model saving completed successfully!\n")
        return {'status': 'success', 'model_path': model_path, 'metrics_path': metrics_path}
        
    except Exception as e:
        logger.error(f"✗ Error saving model: {str(e)}")
        raise

def log_results(**context):
    """Log final results"""
    logger.info("=" * 50)
    logger.info("📝 TASK 4: LOGGING RESULTS")
    logger.info("=" * 50)
    
    try:
        ti = context['task_instance']
        
        # Get all results
        load_result = ti.xcom_pull(task_ids='load_data')
        train_result = ti.xcom_pull(task_ids='train_model')
        save_result = ti.xcom_pull(task_ids='save_model')
        
        logger.info("\n✅ PIPELINE EXECUTION SUMMARY:")
        logger.info(f"   ✓ Data Loading: {load_result['status']}")
        logger.info(f"     - Dataset shape: {load_result['shape']}")
        logger.info(f"   ✓ Model Training: {train_result['status']}")
        logger.info(f"     - Train Accuracy: {train_result['train_accuracy']:.4f}")
        logger.info(f"     - Test Accuracy: {train_result['test_accuracy']:.4f}")
        logger.info(f"   ✓ Model Saving: {save_result['status']}")
        logger.info(f"     - Model Path: {save_result['model_path']}")
        logger.info(f"     - Metrics Path: {save_result['metrics_path']}")
        
        logger.info("\n🎉 ALL TASKS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 50)
        
        return {'status': 'pipeline_complete', 'timestamp': datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"✗ Error logging results: {str(e)}")
        raise

# Define tasks
task_load_data = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)

task_train_model = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

task_save_model = PythonOperator(
    task_id='save_model',
    python_callable=save_model,
    dag=dag,
)

task_log_results = PythonOperator(
    task_id='log_results',
    python_callable=log_results,
    dag=dag,
)

# Set dependencies (task order)
task_load_data >> task_train_model >> task_save_model >> task_log_results
