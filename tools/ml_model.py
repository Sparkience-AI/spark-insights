from smolagents import Tool
import os
import pandas as pd
import numpy as np

class MLModelTool(Tool):
    name = "ml_model_tool"
    description = "Execute Python code to build and evaluate any machine learning model. You have complete freedom to write custom ML code using scikit-learn, tensorflow, or any other ML library."
    inputs = {
        "python_code": {
            "type": "string",
            "description": "Python code to execute for ML tasks. Use 'df' as the DataFrame variable. Save models/results to appropriate directories."
        },
        "df": {
            "type": "object",
            "description": "Pandas DataFrame containing the data for modeling",
            "nullable": True
        }
    }
    output_type = "string"

    def forward(self, python_code: str, df=None) -> str:
        """
        Execute the provided Python code for machine learning tasks.
        
        Available variables in the execution context:
        - df: The input DataFrame
        - np: numpy
        - pd: pandas
        - os: os module
        - sklearn modules: automatically imported when available
        
        The code can save models, results, or outputs as needed.
        """
        
        # Create directories for ML outputs
        os.makedirs('models', exist_ok=True)
        os.makedirs('results', exist_ok=True)
        
        try:
            # Set up the execution environment
            exec_globals = {
                'df': df,
                'np': np,
                'pd': pd,
                'os': os
            }
            
            # Add scikit-learn imports
            try:
                from sklearn.model_selection import train_test_split, cross_val_score
                from sklearn.linear_model import LinearRegression, LogisticRegression
                from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
                from sklearn.cluster import KMeans
                from sklearn.preprocessing import StandardScaler, LabelEncoder
                from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
                
                exec_globals.update({
                    'train_test_split': train_test_split,
                    'cross_val_score': cross_val_score,
                    'LinearRegression': LinearRegression,
                    'LogisticRegression': LogisticRegression,
                    'RandomForestClassifier': RandomForestClassifier,
                    'RandomForestRegressor': RandomForestRegressor,
                    'KMeans': KMeans,
                    'StandardScaler': StandardScaler,
                    'LabelEncoder': LabelEncoder,
                    'accuracy_score': accuracy_score,
                    'mean_squared_error': mean_squared_error,
                    'classification_report': classification_report
                })
            except ImportError:
                pass
            
            # Execute the provided code
            exec(python_code, exec_globals)
            
            return "✅ Successfully executed ML code"
                
        except Exception as e:
            return f"❌ Error executing ML code: {str(e)}"
        """
        INSTRUCTIONS FOR BUILDING MACHINE LEARNING MODELS:

        You have COMPLETE FREEDOM to write and execute any Python code needed to build ML models.
        Use scikit-learn, tensorflow, pytorch, or any other ML library you want.

        MACHINE LEARNING GUIDELINES:
        - ALWAYS follow best practices for model development and evaluation
        - Properly handle data preprocessing (missing values, encoding, scaling)
        - Use appropriate train/validation/test splits
        - Implement cross-validation when possible
        - Handle class imbalance if present
        - Feature engineering and selection when relevant
        - Hyperparameter tuning for better performance
        - Save models and results in organized manner

        COMMON ML TASK TYPES TO CONSIDER:
        - Classification: Binary and multiclass prediction tasks
        - Regression: Continuous value prediction
        - Clustering: Unsupervised grouping of data points
        - Forecasting: Time series prediction
        - Anomaly Detection: Identifying outliers/abnormal patterns
        - Recommendation Systems: Collaborative/user-based filtering
        - Natural Language Processing: Text classification, sentiment analysis
        - Computer Vision: Image classification, object detection
        - Custom ML pipelines: Combining multiple techniques

        MODEL SELECTION GUIDELINES:
        - Choose algorithms appropriate for the data size and type
        - Consider interpretability vs performance trade-offs
        - Use ensemble methods for improved accuracy
        - Try multiple algorithms and compare performance
        - Consider deep learning for complex patterns

        EVALUATION METRICS:
        - Classification: Accuracy, Precision, Recall, F1-Score, AUC-ROC
        - Regression: MSE, RMSE, MAE, R² Score
        - Clustering: Silhouette Score, Calinski-Harabasz Index
        - Forecasting: MAPE, SMAPE, MASE
        - Custom metrics relevant to business goals

        DATA PREPROCESSING CHECKLIST:
        □ Handle missing values appropriately
        □ Encode categorical variables
        □ Scale/normalize numeric features
        □ Feature engineering and selection
        □ Handle outliers if necessary
        □ Check for data leakage
        □ Ensure proper data types

        MODEL VALIDATION:
        □ Use cross-validation for robust evaluation
        □ Test on unseen data
        □ Monitor for overfitting/underfitting
        □ Validate assumptions of chosen algorithms
        □ Consider business metrics beyond accuracy

        FORECASTING SPECIFIC GUIDELINES:
        - Use appropriate time series models (ARIMA, Prophet, LSTM, etc.)
        - Handle seasonality and trends
        - Consider exogenous variables
        - Evaluate forecast accuracy with proper metrics
        - Generate prediction intervals when possible

        CLUSTERING GUIDELINES:
        - Determine optimal number of clusters
        - Use appropriate distance/similarity measures
        - Validate cluster quality with internal/external metrics
        - Interpret and profile resulting clusters

        FILE ORGANIZATION:
        - Save models in 'models/' directory with descriptive names
        - Save evaluation results and metrics
        - Create visualizations of model performance
        - Document model assumptions and limitations

        QUALITY CHECKLIST:
        □ Data properly preprocessed and validated
        □ Model performance thoroughly evaluated
        □ Results are interpretable and actionable
        □ Code is reproducible and well-documented
        □ Model meets business requirements
        □ Performance metrics align with business goals

        Write your machine learning code below following these guidelines:
        """

        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)

        # The LLM should write its ML modeling code here
        # This tool provides complete freedom to build any ML model needed

        return f"ML modeling guidelines provided. Please write and execute custom Python code to build the requested model: '{request}'"
