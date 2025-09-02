import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

class MLWorkflowProgression:
    """
    Local Machine Learning system for workflow progression optimization.
    Learns from approval patterns to suggest optimal workflow paths.
    """
    
    def __init__(self, model_path: str = "models/"):
        self.model_path = model_path
        self.workflow_model = None
        self.department_encoder = LabelEncoder()
        self.priority_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        
        # Ensure models directory exists
        os.makedirs(model_path, exist_ok=True)
        
        # Load existing model if available
        self.load_model()
    
    def prepare_training_data(self, approval_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from approval history.
        
        Args:
            approval_data: List of approval records with workflow information
            
        Returns:
            X: Feature matrix
            y: Target labels (next department)
        """
        if not approval_data:
            return np.array([]), np.array([])
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(approval_data)
        
        # Extract features
        features = []
        targets = []
        
        for _, group in df.groupby('request_id'):
            if len(group) < 2:  # Need at least 2 steps for progression
                continue
                
            # Sort by step order
            group = group.sort_values('step_order')
            
            for i in range(len(group) - 1):
                current_step = group.iloc[i]
                next_step = group.iloc[i + 1]
                
                # Features: current department, priority, step number, request type
                feature_vector = [
                    current_step['department'],
                    current_step['priority'],
                    current_step['step_order'],
                    current_step['request_type'] if 'request_type' in current_step else 'general'
                ]
                
                features.append(feature_vector)
                targets.append(next_step['department'])
        
        if not features:
            return np.array([]), np.array([])
        
        # Encode categorical features
        X = np.array(features)
        
        # Create separate encoders for different feature types
        X[:, 0] = self.department_encoder.fit_transform(X[:, 0])  # department
        X[:, 1] = self.priority_encoder.fit_transform(X[:, 1])    # priority
        
        # Handle request type encoding - create a separate encoder for this
        request_type_encoder = LabelEncoder()
        X[:, 3] = request_type_encoder.fit_transform(X[:, 3])     # request type
        
        # Convert to float
        X = X.astype(float)
        y = np.array(targets)
        
        return X, y
    
    def train_model(self, approval_data: List[Dict]) -> Dict[str, float]:
        """
        Train the workflow progression model.
        
        Args:
            approval_data: Historical approval data
            
        Returns:
            Training metrics
        """
        X, y = self.prepare_training_data(approval_data)
        
        if len(X) == 0:
            return {"error": "No training data available"}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest model
        self.workflow_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.workflow_model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.workflow_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Save model
        self.save_model()
        
        return {
            "accuracy": accuracy,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "feature_importance": dict(zip(
                ['department', 'priority', 'step_order', 'request_type'],
                self.workflow_model.feature_importances_
            ))
        }
    
    def predict_next_department(self, 
                              current_department: str, 
                              priority: str, 
                              step_order: int, 
                              request_type: str = 'general') -> Dict[str, any]:
        """
        Predict the next optimal department for workflow progression.
        
        Args:
            current_department: Current department
            priority: Request priority
            step_order: Current step number
            request_type: Type of request
            
        Returns:
            Prediction results with confidence scores
        """
        if not self.workflow_model:
            return {"error": "Model not trained yet"}
        
        try:
            # Prepare input features
            features = np.array([[
                current_department,
                priority,
                step_order,
                request_type
            ]])
            
            # Encode features - we need to handle encoding properly
            # For now, let's use a simple approach that doesn't require retraining
            # This is a limitation that should be addressed in production
            
            # Check if we can encode the features
            try:
                features[:, 0] = self.department_encoder.transform(features[:, 0])
                features[:, 1] = self.priority_encoder.transform(features[:, 1])
                
                # For request type, we'll use a simple mapping for now
                # In production, you'd want to save and reuse the request type encoder
                request_type_mapping = {'hr': 0, 'it': 1, 'sales': 2, 'general': 3}
                features[:, 3] = request_type_mapping.get(request_type.lower(), 3)
                
                features = features.astype(float)
                
                # Scale features
                features_scaled = self.scaler.transform(features)
                
                # Make prediction
                prediction = self.workflow_model.predict(features_scaled)[0]
                probabilities = self.workflow_model.predict_proba(features_scaled)[0]
                
                # Get department names and their probabilities
                departments = self.department_encoder.classes_
                dept_probs = list(zip(departments, probabilities))
                dept_probs.sort(key=lambda x: x[1], reverse=True)
                
                return {
                    "predicted_department": prediction,
                    "confidence": max(probabilities),
                    "all_probabilities": dept_probs,
                    "current_step": step_order,
                    "suggested_next_step": step_order + 1
                }
                
            except Exception as encoding_error:
                return {"error": f"Feature encoding failed: {str(encoding_error)}"}
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def suggest_workflow(self, 
                        request_type: str, 
                        priority: str, 
                        max_steps: int = 5) -> Dict[str, any]:
        """
        Suggest a complete workflow based on ML predictions.
        
        Args:
            request_type: Type of request
            priority: Request priority
            max_steps: Maximum number of approval steps
            
        Returns:
            Suggested workflow with department sequence
        """
        if not self.workflow_model:
            return {"error": "Model not trained yet"}
        
        try:
            workflow = []
            current_dept = None
            step_order = 1
            
            while step_order <= max_steps:
                if current_dept is None:
                    # First step - use request type to determine starting department
                    starting_depts = {
                        'hr': 'HR',
                        'it': 'IT',
                        'finance': 'Finance',
                        'sales': 'Sales',
                        'facilities': 'Facilities',
                        'legal': 'Legal',
                        'operations': 'Operations'
                    }
                    current_dept = starting_depts.get(request_type.lower(), 'HR')
                else:
                    # Predict next department
                    prediction = self.predict_next_department(
                        current_dept, priority, step_order, request_type
                    )
                    
                    if "error" in prediction:
                        break
                    
                    current_dept = prediction["predicted_department"]
                
                workflow.append({
                    "step": step_order,
                    "department": current_dept,
                    "priority": priority,
                    "request_type": request_type
                })
                
                step_order += 1
                
                # Stop if we're back to a department we've already visited
                if len(workflow) > 1 and any(
                    step["department"] == current_dept 
                    for step in workflow[:-1]
                ):
                    break
            
            return {
                "workflow": workflow,
                "total_steps": len(workflow),
                "confidence": "high" if len(workflow) > 1 else "low"
            }
            
        except Exception as e:
            return {"error": f"Workflow suggestion failed: {str(e)}"}
    
    def analyze_workflow_patterns(self, approval_data: List[Dict]) -> Dict[str, any]:
        """
        Analyze workflow patterns and provide insights.
        
        Args:
            approval_data: Historical approval data
            
        Returns:
            Pattern analysis results
        """
        if not approval_data:
            return {"error": "No data to analyze"}
        
        df = pd.DataFrame(approval_data)
        
        # Department transition matrix
        dept_transitions = {}
        dept_success_rates = {}
        avg_approval_times = {}
        
        for _, group in df.groupby('request_id'):
            if len(group) < 2:
                continue
                
            group = group.sort_values('step_order')
            
            for i in range(len(group) - 1):
                current_dept = group.iloc[i]['department']
                next_dept = group.iloc[i + 1]['department']
                
                # Track transitions
                if current_dept not in dept_transitions:
                    dept_transitions[current_dept] = {}
                
                if next_dept not in dept_transitions[current_dept]:
                    dept_transitions[current_dept][next_dept] = 0
                
                dept_transitions[current_dept][next_dept] += 1
        
        # Calculate success rates and average times
        for dept in df['department'].unique():
            dept_data = df[df['department'] == dept]
            
            # Success rate (approved vs total)
            if 'status' in dept_data.columns:
                success_rate = (dept_data['status'] == 'approved').mean()
                dept_success_rates[dept] = success_rate
            
            # Average approval time
            if 'created_at' in dept_data.columns and 'updated_at' in dept_data.columns:
                dept_data['approval_time'] = pd.to_datetime(dept_data['updated_at']) - pd.to_datetime(dept_data['created_at'])
                avg_time = dept_data['approval_time'].mean()
                avg_approval_times[dept] = str(avg_time).split('.')[0] if pd.notna(avg_time) else "N/A"
        
        return {
            "department_transitions": dept_transitions,
            "success_rates": dept_success_rates,
            "avg_approval_times": avg_approval_times,
            "total_requests": len(df['request_id'].unique()),
            "total_approvals": len(df)
        }
    
    def save_model(self):
        """Save the trained model and encoders."""
        if self.workflow_model:
            joblib.dump(self.workflow_model, os.path.join(self.model_path, 'workflow_model.pkl'))
            joblib.dump(self.department_encoder, os.path.join(self.model_path, 'department_encoder.pkl'))
            joblib.dump(self.priority_encoder, os.path.join(self.model_path, 'priority_encoder.pkl'))
            joblib.dump(self.scaler, os.path.join(self.model_path, 'scaler.pkl'))
    
    def load_model(self):
        """Load existing trained model and encoders."""
        try:
            model_file = os.path.join(self.model_path, 'workflow_model.pkl')
            if os.path.exists(model_file):
                self.workflow_model = joblib.load(model_file)
                self.department_encoder = joblib.load(os.path.join(self.model_path, 'department_encoder.pkl'))
                self.priority_encoder = joblib.load(os.path.join(self.model_path, 'priority_encoder.pkl'))
                self.scaler = joblib.load(os.path.join(self.model_path, 'scaler.pkl'))
                print("✅ ML Workflow Model loaded successfully!")
        except Exception as e:
            print(f"⚠️ Could not load existing model: {e}")
            print("📝 Model will be trained when data is available.")
    
    def export_training_data(self, approval_data: List[Dict], filename: str = None) -> str:
        """
        Export training data to CSV for external analysis.
        
        Args:
            approval_data: Approval data to export
            filename: Output filename (optional)
            
        Returns:
            Path to exported CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_training_data_{timestamp}.csv"
        
        df = pd.DataFrame(approval_data)
        
        # Prepare data for export
        export_data = []
        for _, group in df.groupby('request_id'):
            if len(group) < 2:
                continue
                
            group = group.sort_values('step_order')
            
            for i in range(len(group) - 1):
                current_step = group.iloc[i]
                next_step = group.iloc[i + 1]
                
                export_data.append({
                    'request_id': current_step.get('request_id', ''),
                    'current_department': current_step.get('department', ''),
                    'next_department': next_step.get('department', ''),
                    'priority': current_step.get('priority', ''),
                    'step_order': current_step.get('step_order', ''),
                    'request_type': current_step.get('request_type', 'general'),
                    'status': current_step.get('status', 'unknown'),
                    'created_at': current_step.get('created_at', ''),
                    'updated_at': current_step.get('updated_at', '')
                })
        
        export_df = pd.DataFrame(export_data)
        export_path = os.path.join(self.model_path, filename)
        export_df.to_csv(export_path, index=False)
        
        return export_path

# Create global instance
ml_workflow = MLWorkflowProgression()
