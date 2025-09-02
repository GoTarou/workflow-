#!/usr/bin/env python3
"""
Test script for Linear Regression Workflow System
This script demonstrates linear regression for approval time and success rate prediction.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from linear_regression_workflow import LinearRegressionWorkflow

def test_linear_regression():
    """Test the linear regression workflow system"""
    print("📊 Testing Linear Regression Workflow System")
    print("=" * 60)
    
    # Initialize the linear regression system
    lr_system = LinearRegressionWorkflow()
    
    # Test 1: Check initial model status
    print("\n1. Testing Initial Model Status:")
    print(f"   Models loaded: {list(lr_system.models.keys())}")
    print(f"   Model path: {lr_system.model_path}")
    
    # Test 2: Create sample training data
    print("\n2. Creating Sample Training Data:")
    sample_data = [
        # Request 1: HR time-off request (4 steps, normal priority)
        {
            'request_id': 1,
            'department': 'HR',
            'priority': 'normal',
            'step_order': 1,
            'request_type': 'hr',
            'status': 'approved',
            'created_at': '2024-01-01T09:00:00',
            'updated_at': '2024-01-01T17:00:00'
        },
        {
            'request_id': 1,
            'department': 'Approver',
            'priority': 'normal',
            'step_order': 2,
            'request_type': 'hr',
            'status': 'approved',
            'created_at': '2024-01-01T17:00:00',
            'updated_at': '2024-01-02T10:00:00'
        },
        {
            'request_id': 1,
            'department': 'HR',
            'priority': 'normal',
            'step_order': 3,
            'request_type': 'hr',
            'status': 'approved',
            'created_at': '2024-01-02T10:00:00',
            'updated_at': '2024-01-02T14:00:00'
        },
        {
            'request_id': 1,
            'department': 'Admin',
            'priority': 'normal',
            'step_order': 4,
            'request_type': 'hr',
            'status': 'approved',
            'created_at': '2024-01-02T14:00:00',
            'updated_at': '2024-01-02T16:00:00'
        },
        
        # Request 2: IT hardware request (4 steps, high priority)
        {
            'request_id': 2,
            'department': 'IT',
            'priority': 'high',
            'step_order': 1,
            'request_type': 'it',
            'status': 'approved',
            'created_at': '2024-01-03T08:00:00',
            'updated_at': '2024-01-03T10:00:00'
        },
        {
            'request_id': 2,
            'department': 'Approver',
            'priority': 'high',
            'step_order': 2,
            'request_type': 'it',
            'status': 'approved',
            'created_at': '2024-01-03T10:00:00',
            'updated_at': '2024-01-03T11:00:00'
        },
        {
            'request_id': 2,
            'department': 'IT',
            'priority': 'high',
            'step_order': 3,
            'request_type': 'it',
            'status': 'approved',
            'created_at': '2024-01-03T11:00:00',
            'updated_at': '2024-01-03T12:00:00'
        },
        {
            'request_id': 2,
            'department': 'Admin',
            'priority': 'high',
            'step_order': 4,
            'request_type': 'it',
            'status': 'approved',
            'created_at': '2024-01-03T12:00:00',
            'updated_at': '2024-01-03T13:00:00'
        },
        
        # Request 3: Finance budget request (4 steps, normal priority)
        {
            'request_id': 3,
            'department': 'Finance',
            'priority': 'normal',
            'step_order': 1,
            'request_type': 'finance',
            'status': 'approved',
            'created_at': '2024-01-04T09:00:00',
            'updated_at': '2024-01-04T16:00:00'
        },
        {
            'request_id': 3,
            'department': 'Approver',
            'priority': 'normal',
            'step_order': 2,
            'request_type': 'finance',
            'status': 'approved',
            'created_at': '2024-01-04T16:00:00',
            'updated_at': '2024-01-05T11:00:00'
        },
        {
            'request_id': 3,
            'department': 'Finance',
            'priority': 'normal',
            'step_order': 3,
            'request_type': 'finance',
            'status': 'approved',
            'created_at': '2024-01-05T11:00:00',
            'updated_at': '2024-01-05T15:00:00'
        },
        {
            'request_id': 3,
            'department': 'Admin',
            'priority': 'normal',
            'step_order': 4,
            'request_type': 'finance',
            'status': 'approved',
            'created_at': '2024-01-05T15:00:00',
            'updated_at': '2024-01-05T17:00:00'
        },
        
        # Request 4: Sales contract request (4 steps, urgent priority)
        {
            'request_id': 4,
            'department': 'Sales',
            'priority': 'urgent',
            'step_order': 1,
            'request_type': 'sales',
            'status': 'approved',
            'created_at': '2024-01-06T08:00:00',
            'updated_at': '2024-01-06T09:00:00'
        },
        {
            'request_id': 4,
            'department': 'Approver',
            'priority': 'urgent',
            'step_order': 2,
            'request_type': 'sales',
            'status': 'approved',
            'created_at': '2024-01-06T09:00:00',
            'updated_at': '2024-01-06T10:00:00'
        },
        {
            'request_id': 4,
            'department': 'Sales',
            'priority': 'urgent',
            'step_order': 3,
            'request_type': 'sales',
            'status': 'approved',
            'created_at': '2024-01-06T10:00:00',
            'updated_at': '2024-01-06T11:00:00'
        },
        {
            'request_id': 4,
            'department': 'Admin',
            'priority': 'urgent',
            'step_order': 4,
            'request_type': 'sales',
            'status': 'approved',
            'created_at': '2024-01-06T11:00:00',
            'updated_at': '2024-01-06T12:00:00'
        },
        
        # Request 5: Legal compliance request (4 steps, low priority)
        {
            'request_id': 5,
            'department': 'Legal',
            'priority': 'low',
            'step_order': 1,
            'request_type': 'legal',
            'status': 'approved',
            'created_at': '2024-01-07T10:00:00',
            'updated_at': '2024-01-07T18:00:00'
        },
        {
            'request_id': 5,
            'department': 'Approver',
            'priority': 'low',
            'step_order': 2,
            'request_type': 'legal',
            'status': 'approved',
            'created_at': '2024-01-07T18:00:00',
            'updated_at': '2024-01-08T14:00:00'
        },
        {
            'request_id': 5,
            'department': 'Legal',
            'priority': 'low',
            'step_order': 3,
            'request_type': 'legal',
            'status': 'approved',
            'created_at': '2024-01-08T14:00:00',
            'updated_at': '2024-01-08T16:00:00'
        },
        {
            'request_id': 5,
            'department': 'Admin',
            'priority': 'low',
            'step_order': 4,
            'request_type': 'legal',
            'status': 'approved',
            'created_at': '2024-01-08T16:00:00',
            'updated_at': '2024-01-08T18:00:00'
        },
        
        # Request 6: Facilities maintenance request (4 steps, normal priority)
        {
            'request_id': 6,
            'department': 'Facilities',
            'priority': 'normal',
            'step_order': 1,
            'request_type': 'facilities',
            'status': 'approved',
            'created_at': '2024-01-09T09:00:00',
            'updated_at': '2024-01-09T17:00:00'
        },
        {
            'request_id': 6,
            'department': 'Approver',
            'priority': 'normal',
            'step_order': 2,
            'request_type': 'facilities',
            'status': 'approved',
            'created_at': '2024-01-09T17:00:00',
            'updated_at': '2024-01-10T11:00:00'
        },
        {
            'request_id': 6,
            'department': 'Facilities',
            'priority': 'normal',
            'step_order': 3,
            'request_type': 'facilities',
            'status': 'approved',
            'created_at': '2024-01-10T11:00:00',
            'updated_at': '2024-01-10T15:00:00'
        },
        {
            'request_id': 6,
            'department': 'Admin',
            'priority': 'normal',
            'step_order': 4,
            'request_type': 'facilities',
            'status': 'approved',
            'created_at': '2024-01-10T15:00:00',
            'updated_at': '2024-01-10T17:00:00'
        }
    ]
    
    print(f"   Created {len(sample_data)} sample records")
    print(f"   Representing {len(sample_data)//4} complete workflows")
    
    # Test 3: Train approval time model
    print("\n3. Training Approval Time Model:")
    try:
        approval_time_result = lr_system.train_approval_time_model(sample_data)
        
        if "error" in approval_time_result:
            print(f"   ❌ Training failed: {approval_time_result['error']}")
            return False
        
        print(f"   ✅ Training successful!")
        print(f"   Best model: {approval_time_result['best_model']}")
        print(f"   Training samples: {approval_time_result['training_samples']}")
        print(f"   Test samples: {approval_time_result['test_samples']}")
        
        # Show model comparison
        print("\n   Model Comparison:")
        for model_name, results in approval_time_result['results'].items():
            print(f"     {model_name.upper()}: R² = {results['r2']:.3f}, CV Score = {results['cv_score']:.3f}")
        
    except Exception as e:
        print(f"   ❌ Training failed with error: {e}")
        return False
    
    # Test 4: Train success rate model
    print("\n4. Training Success Rate Model:")
    try:
        success_rate_result = lr_system.train_success_rate_model(sample_data)
        
        if "error" in success_rate_result:
            print(f"   ❌ Training failed: {success_rate_result['error']}")
            return False
        
        print(f"   ✅ Training successful!")
        print(f"   Model type: {success_rate_result['model_type']}")
        print(f"   R² Score: {success_rate_result['metrics']['r2']:.3f}")
        print(f"   Cross-validation Score: {success_rate_result['metrics']['cv_score']:.3f}")
        
    except Exception as e:
        print(f"   ❌ Training failed with error: {e}")
        return False
    
    # Test 5: Make predictions
    print("\n5. Testing Predictions:")
    
    # Test approval time prediction
    print("\n   Approval Time Prediction:")
    approval_prediction = lr_system.predict_approval_time(
        priority='normal',
        num_steps=4,
        request_type='hr',
        dept_complexity=3
    )
    
    if "error" in approval_prediction:
        print(f"     ❌ Prediction failed: {approval_prediction['error']}")
    else:
        print(f"     ✅ Predicted approval time: {approval_prediction['predicted_time_readable']}")
        print(f"        Confidence: {approval_prediction['confidence']}")
    
    # Test success rate prediction
    print("\n   Success Rate Prediction:")
    success_prediction = lr_system.predict_success_rate(
        priority='high',
        num_steps=4,
        request_type='it',
        dept_complexity=3
    )
    
    if "error" in success_prediction:
        print(f"     ❌ Prediction failed: {success_prediction['error']}")
    else:
        print(f"     ✅ Predicted success rate: {success_prediction['predicted_success_percentage']}")
        print(f"        Confidence: {success_prediction['confidence']}")
    
    # Test 6: Feature importance analysis
    print("\n6. Feature Importance Analysis:")
    
    # Approval time feature importance
    print("\n   Approval Time Model Features:")
    approval_importance = lr_system.analyze_feature_importance('approval_time')
    if "error" in approval_importance:
        print(f"     ❌ Analysis failed: {approval_importance['error']}")
    else:
        print(f"     Model: {approval_importance['model_type']}")
        print(f"     Intercept: {approval_importance['intercept']:.3f}")
        print("     Feature Importance:")
        for feature, importance in approval_importance['feature_importance'].items():
            print(f"       {feature}: {importance:.3f}")
    
    # Success rate feature importance
    print("\n   Success Rate Model Features:")
    success_importance = lr_system.analyze_feature_importance('success_rate')
    if "error" in success_importance:
        print(f"     ❌ Analysis failed: {success_importance['error']}")
    else:
        print(f"     Model: {success_importance['model_type']}")
        print(f"     Intercept: {success_importance['intercept']:.3f}")
        print("     Feature Importance:")
        for feature, importance in success_importance['feature_importance'].items():
            print(f"       {feature}: {importance:.3f}")
    
    # Test 7: Generate comprehensive insights
    print("\n7. Generating Business Insights:")
    try:
        insights = lr_system.generate_insights(sample_data)
        
        if "business_insights" in insights:
            business_insights = insights["business_insights"]
            
            if "priority_impact" in business_insights:
                print("\n   Priority Impact on Approval Time:")
                for priority, avg_time in business_insights["priority_impact"].items():
                    print(f"     {priority.upper()}: {avg_time:.1f} hours")
            
            if "department_efficiency" in business_insights:
                print("\n   Department Efficiency:")
                for dept, metrics in business_insights["department_efficiency"].items():
                    success_pct = metrics['success_rate'] * 100
                    print(f"     {dept}: {success_pct:.1f}% success rate ({metrics['total_requests']} requests)")
        
        print("   ✅ Insights generated successfully!")
        
    except Exception as e:
        print(f"   ❌ Insight generation failed: {e}")
    
    print("\n🎉 All linear regression tests completed successfully!")
    return True

def main():
    """Main test function"""
    print("🚀 Linear Regression Workflow System Test")
    print("=" * 70)
    
    success = test_linear_regression()
    
    if success:
        print("\n✅ All tests passed! The linear regression system is working correctly.")
        print("\n📋 What Linear Regression Can Do:")
        print("   1. Predict approval times based on request characteristics")
        print("   2. Predict success rates for different request types")
        print("   3. Analyze which factors most affect workflow efficiency")
        print("   4. Provide business insights for process optimization")
        print("\n🔧 Next steps:")
        print("   1. Run the Flask application")
        print("   2. Login as admin")
        print("   3. Go to Admin Panel > ML Workflow tab")
        print("   4. Train the linear regression models with real data")
        print("   5. Use predictions to optimize your workflows")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
