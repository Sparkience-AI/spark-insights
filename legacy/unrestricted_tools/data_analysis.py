from smolagents import Tool
import pandas as pd
import numpy as np
import os

class DataAnalysisTool(Tool):
    name = "data_analysis_tool"
    description = "Execute Python code for comprehensive data analysis. You have complete freedom to write custom analysis code using pandas, numpy, and statistical libraries."
    inputs = {
        "python_code": {
            "type": "string",
            "description": "Python code to execute for data analysis. Use 'df' as the DataFrame variable. Can perform any analysis needed."
        },
        "df": {
            "type": "object",
            "description": "Pandas DataFrame to analyze",
            "nullable": True
        }
    }
    output_type = "string"

    def forward(self, python_code: str, df=None) -> str:
        """
        Execute the provided Python code for data analysis.
        
        Available variables in the execution context:
        - df: The input DataFrame
        - pd: pandas
        - np: numpy
        - os: os module
        - Common statistical functions
        
        Can perform any analysis: statistics, correlations, distributions, etc.
        """
        
        try:
            # Set up the execution environment
            exec_globals = {
                'df': df,
                'pd': pd,
                'np': np,
                'os': os
            }
            
            # Add statistical imports
            try:
                from scipy import stats
                exec_globals['stats'] = stats
            except ImportError:
                pass
            
            # Execute the provided code and capture output
            from io import StringIO
            import sys
            
            # Capture printed output
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                exec(python_code, exec_globals)
                output = captured_output.getvalue()
            finally:
                sys.stdout = old_stdout
            
            if output.strip():
                return f"✅ Analysis completed:\n{output}"
            else:
                return "✅ Analysis code executed successfully"
                
        except Exception as e:
            return f"❌ Error executing analysis code: {str(e)}"
        """Perform comprehensive data analysis"""
        try:
            analysis_results = []
            
            # Basic statistics
            analysis_results.append("=== BASIC STATISTICS ===")
            analysis_results.append(str(df.describe(include='all')))
            
            # Data types
            analysis_results.append("\n=== DATA TYPES ===")
            analysis_results.append(str(df.dtypes))
            
            # Missing values
            analysis_results.append("\n=== MISSING VALUES ===")
            missing = df.isnull().sum()
            analysis_results.append(str(missing[missing > 0]) if missing.sum() > 0 else "No missing values found")
            
            # Outlier detection (simple IQR method for numeric columns)
            analysis_results.append("\n=== OUTLIER ANALYSIS ===")
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                for col in numeric_cols:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                    analysis_results.append(f"{col}: {outliers} outliers detected")
            else:
                analysis_results.append("No numeric columns for outlier analysis")
            
            # Correlation analysis
            analysis_results.append("\n=== CORRELATION ANALYSIS ===")
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                analysis_results.append(str(corr_matrix))
            else:
                analysis_results.append("Need at least 2 numeric columns for correlation analysis")
            
            return "\n".join(analysis_results)
            
        except Exception as e:
            return f"Error in data analysis: {str(e)}"
