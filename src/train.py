"""
Training script for Iris classification model
Loads dataset, trains a simple classifier, and saves the model
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import json

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# Load dataset
print("Loading dataset...")
df = pd.read_csv('data/dataset.csv')
print(f"Dataset shape: {df.shape}")
print(f"Dataset columns: {list(df.columns)}")

# Separate features and target
X = df.drop('species', axis=1)
y = df['species']

print(f"\nFeatures shape: {X.shape}")
print(f"Target unique values: {y.unique()}")

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set size: {X_train.shape[0]}")
print(f"Test set size: {X_test.shape[0]}")

# Train Random Forest classifier
print("\nTraining Random Forest classifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

print("Model training completed!")

# Make predictions
y_pred = model.predict(X_test)
y_pred_train = model.predict(X_train)

# Calculate accuracy
train_accuracy = accuracy_score(y_train, y_pred_train)
test_accuracy = accuracy_score(y_test, y_pred)

print(f"\nTrain Accuracy: {train_accuracy:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")

# Print detailed classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nFeature Importance:")
print(feature_importance)

# Save the model
model_path = 'models/model.pkl'
joblib.dump(model, model_path)
print(f"\nModel saved to {model_path}")

# Save metrics to JSON file
metrics = {
    'train_accuracy': float(train_accuracy),
    'test_accuracy': float(test_accuracy),
    'training_samples': int(X_train.shape[0]),
    'test_samples': int(X_test.shape[0]),
    'features_used': list(X.columns),
    'classes': list(y.unique())
}

metrics_path = 'models/metrics.json'
with open(metrics_path, 'w') as f:
    json.dump(metrics, f, indent=4)

print(f"Metrics saved to {metrics_path}")
print("\n✅ Training pipeline completed successfully!")
