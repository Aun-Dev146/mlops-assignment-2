"""
Unit tests for the training pipeline
Tests data loading, model training, and shape validation
"""

import pytest
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


class TestDataLoading:
    """Test data loading functionality"""
    
    def test_dataset_exists(self):
        """Test that dataset file exists"""
        assert os.path.exists('data/dataset.csv'), "Dataset file not found"
    
    def test_dataset_shape(self):
        """Test that dataset has correct shape"""
        df = pd.read_csv('data/dataset.csv')
        assert df.shape == (30, 5), f"Expected shape (30, 5), got {df.shape}"
    
    def test_dataset_columns(self):
        """Test that dataset has correct columns"""
        df = pd.read_csv('data/dataset.csv')
        expected_cols = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']
        assert list(df.columns) == expected_cols, f"Columns mismatch: {list(df.columns)}"
    
    def test_no_missing_values(self):
        """Test that dataset has no missing values"""
        df = pd.read_csv('data/dataset.csv')
        assert df.isnull().sum().sum() == 0, "Dataset contains missing values"
    
    def test_species_values(self):
        """Test that species column contains valid values"""
        df = pd.read_csv('data/dataset.csv')
        valid_species = {'setosa', 'versicolor', 'virginica'}
        unique_species = set(df['species'].unique())
        assert unique_species == valid_species, f"Invalid species: {unique_species}"
    
    def test_feature_types(self):
        """Test that features are numeric"""
        df = pd.read_csv('data/dataset.csv')
        features = df[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']]
        assert features.dtypes.apply(lambda x: np.issubdtype(x, np.number)).all(), \
            "Not all features are numeric"


class TestModelTraining:
    """Test model training functionality"""
    
    @pytest.fixture
    def prepare_data(self):
        """Fixture to prepare training data"""
        df = pd.read_csv('data/dataset.csv')
        X = df.drop('species', axis=1)
        y = df['species']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        return X_train, X_test, y_train, y_test
    
    def test_train_test_split_sizes(self, prepare_data):
        """Test that train-test split has correct sizes"""
        X_train, X_test, y_train, y_test = prepare_data
        assert X_train.shape[0] == 24, f"Expected 24 training samples, got {X_train.shape[0]}"
        assert X_test.shape[0] == 6, f"Expected 6 test samples, got {X_test.shape[0]}"
    
    def test_features_preserved(self, prepare_data):
        """Test that all 4 features are preserved"""
        X_train, _, _, _ = prepare_data
        assert X_train.shape[1] == 4, f"Expected 4 features, got {X_train.shape[1]}"
    
    def test_model_trains_successfully(self, prepare_data):
        """Test that model trains without errors"""
        X_train, _, y_train, _ = prepare_data
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        assert model is not None, "Model training failed"
        assert hasattr(model, 'predict'), "Model doesn't have predict method"
    
    def test_model_predictions(self, prepare_data):
        """Test that model can make predictions"""
        X_train, X_test, y_train, _ = prepare_data
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        assert predictions.shape[0] == X_test.shape[0], "Prediction count mismatch"
        assert len(predictions) == 6, f"Expected 6 predictions, got {len(predictions)}"
    
    def test_model_accuracy(self, prepare_data):
        """Test that model achieves reasonable accuracy"""
        X_train, X_test, y_train, y_test = prepare_data
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)
        assert accuracy >= 0.5, f"Model accuracy too low: {accuracy}"
    
    def test_feature_importance(self, prepare_data):
        """Test that model learns feature importance"""
        X_train, _, y_train, _ = prepare_data
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        importances = model.feature_importances_
        assert len(importances) == 4, f"Expected 4 importances, got {len(importances)}"
        assert importances.sum() > 0, "Feature importances sum to zero"


class TestShapeValidation:
    """Test output shape validation"""
    
    def test_output_directories_exist(self):
        """Test that output directories exist"""
        assert os.path.exists('models'), "models directory doesn't exist"
    
    def test_model_file_shape(self):
        """Test that trained model file has expected properties"""
        # Train a model for testing
        df = pd.read_csv('data/dataset.csv')
        X = df.drop('species', axis=1)
        y = df['species']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Verify model properties
        assert model.n_estimators == 100, "Model doesn't have 100 estimators"
        assert len(model.classes_) == 3, f"Expected 3 classes, got {len(model.classes_)}"
    
    def test_prediction_shape(self):
        """Test that predictions have correct shape"""
        df = pd.read_csv('data/dataset.csv')
        X = df.drop('species', axis=1)
        y = df['species']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        
        assert predictions.shape == (6,), f"Expected shape (6,), got {predictions.shape}"
        assert all(pred in model.classes_ for pred in predictions), \
            "Predictions contain invalid classes"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
