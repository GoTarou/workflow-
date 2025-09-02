import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import joblib
import os
from typing import Dict, List, Tuple, Optional
import json

class LinearRegressionWorkflow:
    """
    Linear Regression system for workflow analytics and predictions.
    Predicts approval times, success rates, and workflow efficiency metrics.
    """
    
    def __init__(self, model_path: str = "models/"):
        self.model_path = model_path
        self.models = {}
        self.scalers = {}
        self.feature_names = {}
        
        # Ensure models directory exists
        os.makedirs(model_path, exist_ok=True)
        
        # Load existing models if available
        self.load_models()
    
    def prepare_approval_time_data(self, approval_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for predicting approval times.
        
        Features:
        - Request priority (encoded)
        - Number of approval steps
        - Request type (encoded)
        - Department complexity
        - Day of week
        - Time of day
        
        Target: Approval time in hours
        """
        if not approval_data:
            return np.array([]), np.array([])
        
        df = pd.DataFrame(approval_data)
        
        # Calculate approval time for each request
        features = []
        targets = []
        
        for _, group in df.groupby('request_id'):
            if len(group) < 2:  # Need at least 2 steps
                continue
            
            # Calculate total approval time
            start_time = pd.to_datetime(group['created_at'].min())
            end_time = pd.to_datetime(group['updated_at'].max())
            approval_time_hours = (end_time - start_time).total_seconds() / 3600
            
            # Extract features
            request_data = group.iloc[0]  # First record has request details
            
            # Priority encoding
            priority_mapping = {'low': 1, 'normal': 2, 'high': 3, 'urgent': 4}
            priority_encoded = priority_mapping.get(request_data.get('priority', 'normal'), 2)
            
            # Request type encoding
            request_type = request_data.get('request_type', 'general')
            type_mapping = {'hr': 1, 'it': 2, 'finance': 3, 'sales': 4, 'facilities': 5, 'legal': 6, 'operations': 7}
            type_encoded = type_mapping.get(request_type.lower(), 1)
            
            # Number of approval steps
            num_steps = len(group)
            
            # Department complexity (number of unique departments)
            unique_depts = group['department'].nunique()
            
            # Time features
            start_dt = pd.to_datetime(start_time)
            day_of_week = start_dt.weekday()  # 0=Monday, 6=Sunday
            time_of_day = start_dt.hour  # 0-23
            
            # Create feature vector
            feature_vector = [
                priority_encoded,
                num_steps,
                type_encoded,
                unique_depts,
                day_of_week,
                time_of_day
            ]
            
            features.append(feature_vector)
            targets.append(approval_time_hours)
        
        if not features:
            return np.array([]), np.array([])
        
        X = np.array(features)
        y = np.array(targets)
        
        return X, y
    
    def prepare_success_rate_data(self, approval_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for predicting success rates.
        
        Features:
        - Request priority
        - Number of approval steps
        - Request type
        - Department complexity
        - Previous success rate for similar requests
        
        Target: Success rate (0-1)
        """
        if not approval_data:
            return np.array([]), np.array([])
        
        df = pd.DataFrame(approval_data)
        
        features = []
        targets = []
        
        for _, group in df.groupby('request_id'):
            if len(group) < 2:
                continue
            
            request_data = group.iloc[0]
            
            # Priority encoding
            priority_mapping = {'low': 1, 'normal': 2, 'high': 3, 'urgent': 4}
            priority_encoded = priority_mapping.get(request_data.get('priority', 'normal'), 2)
            
            # Request type encoding
            request_type = request_data.get('request_type', 'general')
            type_mapping = {'hr': 1, 'it': 2, 'finance': 3, 'sales': 4, 'facilities': 5, 'legal': 6, 'operations': 7}
            type_encoded = type_mapping.get(request_type.lower(), 1)
            
            # Number of approval steps
            num_steps = len(group)
            
            # Department complexity
            unique_depts = group['department'].nunique()
            
            # Calculate success rate for this request
            approved_steps = (group['status'] == 'approved').sum()
            success_rate = approved_steps / len(group)
            
            # Feature vector
            feature_vector = [
                priority_encoded,
                num_steps,
                type_encoded,
                unique_depts
            ]
            
            features.append(feature_vector)
            targets.append(success_rate)
        
        if not features:
            return np.array([]), np.array([])
        
        X = np.array(features)
        y = np.array(targets)
        
        return X, y
    
    def train_approval_time_model(self, approval_data: List[Dict]) -> Dict[str, any]:
        """
        Train linear regression model to predict approval times.
        """
        X, y = self.prepare_approval_time_data(approval_data)
        
        if len(X) == 0:
            return {"error": "No training data available for approval time prediction"}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'linear': LinearRegression(),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.1)
        }
        
        best_model = None
        best_score = -float('inf')
        results = {}
        
        for name, model in models.items():
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=min(3, len(X_train)))
            cv_mean = cv_scores.mean()
            
            results[name] = {
                'mse': mse,
                'r2': r2,
                'mae': mae,
                'cv_score': cv_mean
            }
            
            # Track best model (use R² score if CV score is NaN)
            if not np.isnan(cv_mean) and cv_mean > best_score:
                best_score = cv_mean
                best_model = model
            elif np.isnan(cv_mean) and best_model is None:
                # If no CV score available, use R² score as fallback
                if r2 > best_score:
                    best_score = r2
                    best_model = model
        
        # If still no best model, use the first one
        if best_model is None:
            best_model = models['linear']
            best_score = results['linear']['r2']
            print(f"⚠️ Using fallback model selection due to insufficient data")
        
        # Save best model
        self.models['approval_time'] = best_model
        self.scalers['approval_time'] = scaler
        self.feature_names['approval_time'] = [
            'priority', 'num_steps', 'request_type', 'dept_complexity', 'day_of_week', 'time_of_day'
        ]
        
        # Save models
        self.save_models()
        
        return {
            "success": True,
            "best_model": best_model.__class__.__name__,
            "results": results,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "feature_names": self.feature_names['approval_time']
        }
    
    def train_success_rate_model(self, approval_data: List[Dict]) -> Dict[str, any]:
        """
        Train linear regression model to predict success rates.
        """
        X, y = self.prepare_success_rate_data(approval_data)
        
        if len(X) == 0:
            return {"error": "No training data available for success rate prediction"}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=min(3, len(X_train)))
        cv_mean = cv_scores.mean()
        
        # Save model
        self.models['success_rate'] = model
        self.scalers['success_rate'] = scaler
        self.feature_names['success_rate'] = [
            'priority', 'num_steps', 'request_type', 'dept_complexity'
        ]
        
        # Save models
        self.save_models()
        
        return {
            "success": True,
            "model_type": model.__class__.__name__,
            "metrics": {
                'mse': mse,
                'r2': r2,
                'mae': mae,
                'cv_score': cv_mean
            },
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "feature_names": self.feature_names['success_rate']
        }
    
    def predict_approval_time(self, 
                             priority: str, 
                             num_steps: int, 
                             request_type: str, 
                             dept_complexity: int,
                             day_of_week: int = None,
                             time_of_day: int = None) -> Dict[str, any]:
        """
        Predict approval time for a new request.
        """
        if 'approval_time' not in self.models:
            return {"error": "Approval time model not trained yet"}
        
        # Set default values if not provided
        if day_of_week is None:
            day_of_week = datetime.now().weekday()
        if time_of_day is None:
            time_of_day = datetime.now().hour
        
        # Prepare features
        priority_mapping = {'low': 1, 'normal': 2, 'high': 3, 'urgent': 4}
        priority_encoded = priority_mapping.get(priority.lower(), 2)
        
        type_mapping = {'hr': 1, 'it': 2, 'finance': 3, 'sales': 4, 'facilities': 5, 'legal': 6, 'operations': 7}
        type_encoded = type_mapping.get(request_type.lower(), 1)
        
        features = np.array([[
            priority_encoded,
            num_steps,
            type_encoded,
            dept_complexity,
            day_of_week,
            time_of_day
        ]])
        
        # Scale features
        features_scaled = self.scalers['approval_time'].transform(features)
        
        # Make prediction
        prediction = self.models['approval_time'].predict(features_scaled)[0]
        
        # Convert to readable format
        if prediction < 24:
            time_str = f"{prediction:.1f} hours"
        else:
            days = prediction / 24
            time_str = f"{days:.1f} days"
        
        return {
            "predicted_time_hours": prediction,
            "predicted_time_readable": time_str,
            "confidence": "high" if prediction > 0 else "low",
            "features_used": self.feature_names['approval_time']
        }
    
    def predict_success_rate(self, 
                            priority: str, 
                            num_steps: int, 
                            request_type: str, 
                            dept_complexity: int) -> Dict[str, any]:
        """
        Predict success rate for a new request.
        """
        if 'success_rate' not in self.models:
            return {"error": "Success rate model not trained yet"}
        
        # Prepare features
        priority_mapping = {'low': 1, 'normal': 2, 'high': 3, 'urgent': 4}
        priority_encoded = priority_mapping.get(priority.lower(), 2)
        
        type_mapping = {'hr': 1, 'it': 2, 'finance': 3, 'sales': 4, 'facilities': 5, 'legal': 6, 'operations': 7}
        type_encoded = type_mapping.get(request_type.lower(), 1)
        
        features = np.array([[
            priority_encoded,
            num_steps,
            type_encoded,
            dept_complexity
        ]])
        
        # Scale features
        features_scaled = self.scalers['success_rate'].transform(features)
        
        # Make prediction
        prediction = self.models['success_rate'].predict(features_scaled)[0]
        
        # Ensure prediction is between 0 and 1
        prediction = max(0, min(1, prediction))
        
        return {
            "predicted_success_rate": prediction,
            "predicted_success_percentage": f"{prediction * 100:.1f}%",
            "confidence": "high" if 0 <= prediction <= 1 else "low",
            "features_used": self.feature_names['success_rate']
        }
    
    def analyze_feature_importance(self, model_name: str = 'approval_time') -> Dict[str, any]:
        """
        Analyze feature importance for linear regression models.
        """
        if model_name not in self.models:
            return {"error": f"Model {model_name} not found"}
        
        model = self.models[model_name]
        feature_names = self.feature_names[model_name]
        
        if hasattr(model, 'coef_'):
            # Get coefficients (feature importance)
            coefficients = model.coef_
            
            # Create feature importance dictionary
            feature_importance = dict(zip(feature_names, coefficients))
            
            # Sort by absolute importance
            sorted_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)
            
            return {
                "model": model_name,
                "feature_importance": dict(sorted_features),
                "intercept": float(model.intercept_) if hasattr(model, 'intercept_') else 0,
                "model_type": model.__class__.__name__
            }
        else:
            return {"error": "Model doesn't support coefficient analysis"}
    
    def generate_insights(self, approval_data: List[Dict]) -> Dict[str, any]:
        """
        Generate insights from linear regression analysis.
        """
        insights = {}
        
        # Train models if not already trained
        if 'approval_time' not in self.models:
            approval_time_result = self.train_approval_time_model(approval_data)
            if "success" in approval_time_result:
                insights["approval_time_training"] = approval_time_result
        
        if 'success_rate' not in self.models:
            success_rate_result = self.train_success_rate_model(approval_data)
            if "success" in success_rate_result:
                insights["success_rate_training"] = success_rate_result
        
        # Analyze feature importance
        if 'approval_time' in self.models:
            insights["approval_time_analysis"] = self.analyze_feature_importance('approval_time')
        
        if 'success_rate' in self.models:
            insights["success_rate_analysis"] = self.analyze_feature_importance('success_rate')
        
        # Generate business insights
        insights["business_insights"] = self._generate_business_insights(approval_data)
        
        return insights
    
    def _generate_business_insights(self, approval_data: List[Dict]) -> Dict[str, any]:
        """
        Generate business insights from the data.
        """
        if not approval_data:
            return {"error": "No data available for analysis"}
        
        df = pd.DataFrame(approval_data)
        
        insights = {}
        
        # Priority impact on approval time
        if 'priority' in df.columns and 'created_at' in df.columns and 'updated_at' in df.columns:
            priority_times = {}
            for priority in df['priority'].unique():
                priority_data = df[df['priority'] == priority]
                if len(priority_data) > 0:
                    # Calculate average approval time for this priority
                    times = []
                    for _, group in priority_data.groupby('request_id'):
                        if len(group) >= 2:
                            start_time = pd.to_datetime(group['created_at'].min())
                            end_time = pd.to_datetime(group['updated_at'].max())
                            approval_time = (end_time - start_time).total_seconds() / 3600
                            times.append(approval_time)
                    
                    if times:
                        priority_times[priority] = np.mean(times)
            
            insights["priority_impact"] = priority_times
        
        # Department efficiency
        if 'department' in df.columns:
            dept_efficiency = {}
            for dept in df['department'].unique():
                dept_data = df[df['department'] == dept]
                if len(dept_data) > 0:
                    # Calculate success rate for this department
                    success_rate = (dept_data['status'] == 'approved').mean()
                    dept_efficiency[dept] = {
                        'success_rate': success_rate,
                        'total_requests': len(dept_data)
                    }
            
            insights["department_efficiency"] = dept_efficiency
        
        return insights
    
    def save_models(self):
        """Save all trained models and scalers."""
        for name, model in self.models.items():
            model_path = os.path.join(self.model_path, f'{name}_model.pkl')
            joblib.dump(model, model_path)
        
        for name, scaler in self.scalers.items():
            scaler_path = os.path.join(self.model_path, f'{name}_scaler.pkl')
            joblib.dump(scaler, scaler_path)
        
        # Save feature names
        feature_path = os.path.join(self.model_path, 'feature_names.json')
        with open(feature_path, 'w') as f:
            json.dump(self.feature_names, f)
    
    def load_models(self):
        """Load existing trained models and scalers."""
        try:
            # Load feature names
            feature_path = os.path.join(self.model_path, 'feature_names.json')
            if os.path.exists(feature_path):
                with open(feature_path, 'r') as f:
                    self.feature_names = json.load(f)
            
            # Load models
            for name in ['approval_time', 'success_rate']:
                model_path = os.path.join(self.model_path, f'{name}_model.pkl')
                scaler_path = os.path.join(self.model_path, f'{name}_scaler.pkl')
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    self.models[name] = joblib.load(model_path)
                    self.scalers[name] = joblib.load(scaler_path)
                    print(f"✅ {name} model loaded successfully!")
            
        except Exception as e:
            print(f"⚠️ Could not load existing models: {e}")
            print("📝 Models will be trained when data is available.")

# Create global instance
linear_regression_workflow = LinearRegressionWorkflow()
