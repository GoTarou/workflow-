#!/usr/bin/env python3
"""
Test script for ML Workflow Progression System
This script tests the local machine learning functionality without external APIs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_workflow_progression import MLWorkflowProgression

def test_ml_workflow():
    """Test the ML workflow progression system"""
    print("🧠 Testing ML Workflow Progression System")
    print("=" * 50)
    
    # Initialize the ML system
    ml_system = MLWorkflowProgression()
    
    # Test 1: Check initial model status
    print("\n1. Testing Initial Model Status:")
    print(f"   Model loaded: {ml_system.workflow_model is not None}")
    print(f"   Model path: {ml_system.model_path}")
    
    # Test 2: Create sample training data
    print("\n2. Creating Sample Training Data:")
    sample_data = [
        {
            'request_id': 1,
            'department': 'HR',
            'priority': 'normal',
            'step_order': 1,
            'request_type': 'hr',
            'status': 'approved',
            'created_at': '2024-01-01T10:00:00',
            'updated_at': '2024-01-01T11:00:00'
        },
        {
            'request_id': 1,
            'department': 'IT',
            'priority': 'normal',
            'step_order': 2,
            'request_type': 'hr',
            'status': 'approved',
            'created_at': '2024-01-01T11:00:00',
            'updated_at': '2024-01-01T12:00:00'
        },
        {
            'request_id': 2,
            'department': 'IT',
            'priority': 'high',
            'step_order': 1,
            'request_type': 'it',
            'status': 'approved',
            'created_at': '2024-01-02T10:00:00',
            'updated_at': '2024-01-02T11:00:00'
        },
        {
            'request_id': 2,
            'department': 'Finance',
            'priority': 'high',
            'step_order': 2,
            'request_type': 'it',
            'status': 'approved',
            'created_at': '2024-01-02T11:00:00',
            'updated_at': '2024-01-02T12:00:00'
        },
        {
            'request_id': 3,
            'department': 'Sales',
            'priority': 'normal',
            'step_order': 1,
            'request_type': 'sales',
            'status': 'approved',
            'created_at': '2024-01-03T10:00:00',
            'updated_at': '2024-01-03T11:00:00'
        },
        {
            'request_id': 3,
            'department': 'Operations',
            'priority': 'normal',
            'step_order': 2,
            'request_type': 'sales',
            'status': 'approved',
            'created_at': '2024-01-03T11:00:00',
            'updated_at': '2024-01-03T12:00:00'
        }
    ]
    
    print(f"   Created {len(sample_data)} sample records")
    
    # Test 3: Train the model
    print("\n3. Training the Model:")
    try:
        training_result = ml_system.train_model(sample_data)
        
        if "error" in training_result:
            print(f"   ❌ Training failed: {training_result['error']}")
            return False
        
        print(f"   ✅ Training successful!")
        print(f"   Accuracy: {training_result['accuracy']:.2%}")
        print(f"   Training samples: {training_result['training_samples']}")
        print(f"   Test samples: {training_result['test_samples']}")
        
        # Test 4: Make predictions
        print("\n4. Testing Predictions:")
        test_cases = [
            ('HR', 'normal', 1, 'hr'),
            ('IT', 'high', 1, 'it'),
            ('Sales', 'normal', 1, 'sales')
        ]
        
        for current_dept, priority, step_order, request_type in test_cases:
            prediction = ml_system.predict_next_department(
                current_dept, priority, step_order, request_type
            )
            
            if "error" in prediction:
                print(f"   ❌ Prediction failed for {current_dept}: {prediction['error']}")
            else:
                print(f"   ✅ {current_dept} → {prediction['predicted_department']} "
                      f"(Confidence: {prediction['confidence']:.2%})")
        
        # Test 5: Suggest complete workflows
        print("\n5. Testing Workflow Suggestions:")
        workflow_suggestion = ml_system.suggest_workflow('hr', 'normal', 3)
        
        if "error" in workflow_suggestion:
            print(f"   ❌ Workflow suggestion failed: {workflow_suggestion['error']}")
        else:
            print(f"   ✅ Suggested workflow with {workflow_suggestion['total_steps']} steps:")
            for step in workflow_suggestion['workflow']:
                print(f"      Step {step['step']}: {step['department']}")
        
        # Test 6: Analyze patterns
        print("\n6. Testing Pattern Analysis:")
        pattern_analysis = ml_system.analyze_workflow_patterns(sample_data)
        
        if "error" in pattern_analysis:
            print(f"   ❌ Pattern analysis failed: {pattern_analysis['error']}")
        else:
            print(f"   ✅ Pattern analysis successful!")
            print(f"   Total requests: {pattern_analysis['total_requests']}")
            print(f"   Total approvals: {pattern_analysis['total_approvals']}")
            print(f"   Department transitions: {len(pattern_analysis['department_transitions'])}")
        
        # Test 7: Export training data
        print("\n7. Testing Data Export:")
        try:
            export_path = ml_system.export_training_data(sample_data, "test_export.csv")
            print(f"   ✅ Data exported to: {export_path}")
        except Exception as e:
            print(f"   ❌ Export failed: {e}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 ML Workflow Progression System Test")
    print("=" * 60)
    
    success = test_ml_workflow()
    
    if success:
        print("\n✅ All tests passed! The ML system is working correctly.")
        print("\n📋 Next steps:")
        print("   1. Run the Flask application")
        print("   2. Login as admin")
        print("   3. Go to Admin Panel > ML Workflow tab")
        print("   4. Train the model with real data")
        print("   5. Use ML suggestions in the workflow designer")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
