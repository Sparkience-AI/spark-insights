from smolagents import Tool
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta

class VisualizationTool(Tool):
    name = "visualization_tool"
    description = "Execute Python code to create any visualization. You have complete freedom to write matplotlib/seaborn code to generate charts and save them as PNG files."
    inputs = {
        "python_code": {
            "type": "string",
            "description": "Python code to execute for creating visualizations. Use 'df' as the DataFrame variable. Save plots to 'plots/' directory with descriptive filenames."
        },
        "df": {
            "type": "object",
            "description": "Pandas DataFrame containing the data to visualize",
            "nullable": True
        }
    }
    output_type = "string"

    def forward(self, python_code: str, df=None) -> str:
        """
        Execute the provided Python code to create visualizations.
        
        Available variables in the execution context:
        - df: The input DataFrame
        - plt: matplotlib.pyplot
        - sns: seaborn
        - np: numpy
        - pd: pandas
        - os: os module
        - df_clean: cleaned df
        
        The code should save plots to the 'plots/' directory.
        """
        
        # Create plots directory if it doesn't exist
        os.makedirs('plots', exist_ok=True)
        
        try:
            # Set up the execution environment
            exec_globals = {
                'df': df,
                'plt': plt,
                'sns': sns, 
                'np': np,
                'pd': pd,
                'os': os,
                'datetime': datetime,
                'timedelta': timedelta
            }
            
            # Add sklearn imports for common ML tasks
            try:
                from sklearn.linear_model import LinearRegression
                from sklearn.cluster import KMeans
                from sklearn.preprocessing import StandardScaler
                exec_globals.update({
                    'LinearRegression': LinearRegression,
                    'KMeans': KMeans,
                    'StandardScaler': StandardScaler
                })
            except ImportError:
                pass
            
            # Execute the provided code
            exec(python_code, exec_globals)
            
            # Check what files were created
            if os.path.exists('plots'):
                plot_files = [f for f in os.listdir('plots') if f.endswith('.png')]
                if plot_files:
                    # Sort by creation time but return ALL files, not just 3
                    all_files = sorted(plot_files, key=lambda x: os.path.getctime(f'plots/{x}'), reverse=True)
                    return f"✅ Successfully created visualizations. Generated {len(all_files)} files: {', '.join(all_files)}"
                else:
                    return "⚠️ Code executed but no PNG files were found in plots/ directory"
            else:
                return "⚠️ Code executed but plots/ directory was not found"
                
        except Exception as e:
            return f"❌ Error executing visualization code: {str(e)}"
