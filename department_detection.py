import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
import joblib
import os

class DepartmentDetection:
    """
    ML model for detecting the appropriate department based on request description/phrase
    """
    
    def __init__(self):
        self.model_path = 'models/department_detection_model.pkl'
        self.vectorizer_path = 'models/department_detection_vectorizer.pkl'
        self.model = None
        self.vectorizer = None
        self.departments = []
        
        # Ensure models directory exists
        os.makedirs('models', exist_ok=True)
        
        # Try to load existing model
        self.load_model()
    
    def load_model(self):
        """Load existing trained model if available"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                print(f"✅ Department detection model loaded from {self.model_path}")
                return True
        except Exception as e:
            print(f"⚠️ Could not load existing model: {e}")
        
        return False
    
    def save_model(self):
        """Save the trained model and vectorizer"""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.vectorizer, self.vectorizer_path)
            print(f"✅ Model saved to {self.model_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to save model: {e}")
            return False
    
    def train_model(self, training_data):
        """
        Train the department detection model
        
        Args:
            training_data: List of dicts with 'phrase' and 'department' keys
            
        Returns:
            dict: Training results and metrics
        """
        try:
            if not training_data:
                return {"error": "No training data provided"}
            
            # Convert to DataFrame
            df = pd.DataFrame(training_data)
            
            # Validate data
            if 'phrase' not in df.columns or 'department' not in df.columns:
                return {"error": "Training data must contain 'phrase' and 'department' columns"}
            
            # Get unique departments
            self.departments = sorted(df['department'].unique())
            
            if len(self.departments) < 2:
                return {"error": "Need at least 2 different departments for training"}
            
            print(f"🎯 Training department detection model for: {', '.join(self.departments)}")
            print(f"📊 Training samples: {len(df)}")
            
            # Split data
            X = df['phrase']
            y = df['department']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Create pipeline with TF-IDF vectorizer and classifier
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),  # Use unigrams and bigrams
                min_df=2,  # Minimum document frequency
                max_df=0.95  # Maximum document frequency
            )
            
            # Try different classifiers
            classifiers = {
                'MultinomialNB': MultinomialNB(),
                'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42)
            }
            
            best_score = 0
            best_classifier = None
            best_name = None
            
            for name, classifier in classifiers.items():
                # Create pipeline
                pipeline = Pipeline([
                    ('vectorizer', self.vectorizer),
                    ('classifier', classifier)
                ])
                
                # Train
                pipeline.fit(X_train, y_train)
                
                # Evaluate
                y_pred = pipeline.predict(X_test)
                score = accuracy_score(y_test, y_pred)
                
                print(f"📈 {name} accuracy: {score:.3f}")
                
                if score > best_score:
                    best_score = score
                    best_classifier = classifier
                    best_name = name
            
            # Use best classifier
            self.model = Pipeline([
                ('vectorizer', self.vectorizer),
                ('classifier', best_classifier)
            ])
            
            # Final training on full dataset
            self.model.fit(X, y)
            
            # Final evaluation
            y_pred = self.model.predict(X_test)
            final_accuracy = accuracy_score(y_test, y_pred)
            
            # Generate classification report
            report = classification_report(y_test, y_pred, output_dict=True)
            
            # Save model
            self.save_model()
            
            return {
                "success": True,
                "model_type": best_name,
                "accuracy": final_accuracy,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "departments": self.departments,
                "classification_report": report
            }
            
        except Exception as e:
            return {"error": f"Training failed: {str(e)}"}
    
    def predict_department(self, phrase):
        """
        Predict the department for a given phrase
        
        Args:
            phrase: String description of the request
            
        Returns:
            dict: Prediction results
        """
        try:
            if self.model is None:
                return {"error": "Model not trained. Please train the model first."}
            
            if not phrase or not phrase.strip():
                return {"error": "Phrase cannot be empty"}
            
            # Make prediction
            predicted_department = self.model.predict([phrase])[0]
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba([phrase])[0]
            
            # Create department-probability pairs
            dept_probs = list(zip(self.departments, probabilities))
            dept_probs.sort(key=lambda x: x[1], reverse=True)
            
            # Get confidence (highest probability)
            confidence = max(probabilities)
            
            return {
                "predicted_department": predicted_department,
                "confidence": confidence,
                "all_probabilities": dept_probs,
                "phrase": phrase
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def get_model_info(self):
        """Get information about the current model"""
        if self.model is None:
            return {
                "model_loaded": False,
                "message": "No model trained yet"
            }
        
        return {
            "model_loaded": True,
            "model_type": type(self.model.named_steps['classifier']).__name__,
            "departments": self.departments,
            "vectorizer_features": self.vectorizer.get_feature_names_out().shape[0] if hasattr(self.vectorizer, 'get_feature_names_out') else "Unknown",
            "model_path": self.model_path
        }
    
    def test_sample_phrases(self):
        """Test the model with some sample phrases"""
        if self.model is None:
            return {"error": "Model not trained"}
        
        sample_phrases = [
            "I need time off next week",
            "My laptop is not working",
            "Can I submit an expense report?",
            "The AC is broken in my office",
            "How do I apply for vacation?",
            "I forgot my password",
            "When will I get paid?",
            "The printer is jammed"
        ]
        
        results = []
        for phrase in sample_phrases:
            prediction = self.predict_department(phrase)
            if "error" not in prediction:
                results.append({
                    "phrase": phrase,
                    "predicted": prediction["predicted_department"],
                    "confidence": f"{prediction['confidence']:.1%}"
                })
        
        return {
            "success": True,
            "sample_predictions": results
        }
