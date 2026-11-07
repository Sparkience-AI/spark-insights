#!/usr/bin/env python3
"""
Code Agent using smolagents with OpenAI GPT-4o-mini
Main entry point for the AI Data Scientist Assistant
"""

from smolagents import CodeAgent, DuckDuckGoSearchTool, OpenAIServerModel, PythonInterpreterTool, WebSearchTool, WikipediaSearchTool, BaseTool
import os
import json
from dotenv import load_dotenv
from tools.file_handler import FileHandlerTool
from tools.data_analysis import DataAnalysisTool
from tools.ml_model import MLModelTool
from tools.visualization import VisualizationTool
from tools.report_generator import ReportGeneratorTool
from tools.conversation_manager import ConversationManagerTool
from config import model, additional_authorized_imports, system_prompt
from agent import agent

load_dotenv()

# Custom Tools are now imported from separate modules
# Model, agent, and system prompt are now imported from separate modules

# Welcome message
print("🚀 Welcome to Insight! Your AI Data Scientist Assistant.\n")

# Ask for data file path
data_path = input("📁 Please provide your data file path (CSV/Excel):\n> ")

# Ask for business goal
business_goal = input("🎯 What is your business goal for this analysis?\n> ")

# Run the complete analysis workflow automatically
final_result = agent.run(f"{system_prompt}\n\nBusiness Goal: {business_goal}\nData File: {data_path}\n\nExecute the complete 4-phase analysis workflow and return the final JSON report using final_answer(). Do NOT generate any PowerPoint presentations during this analysis.")

print(f"\n📊 Final Analysis Results:\n{final_result}")

# Generate PowerPoint presentation by having the agent write the code
print("\n📊 Generating PowerPoint presentation...")
try:
    # Parse the final result to extract the JSON
    if isinstance(final_result, str):
        # Try to find JSON content in the string
        if final_result.startswith('{'):
            import json
            analysis_data = json.loads(final_result)
        elif 'final_answer' in final_result:
            # Extract content after 'final_answer'
            try:
                start_idx = final_result.find('{')
                end_idx = final_result.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = final_result[start_idx:end_idx]
                    analysis_data = json.loads(json_str)
                else:
                    analysis_data = {}
            except:
                analysis_data = {}
        else:
            analysis_data = {}
    else:
        # If it's already a dict, use it directly
        analysis_data = final_result if isinstance(final_result, dict) else {}
    
    if analysis_data and isinstance(analysis_data, dict):
        # Get list of available visualization files
        import glob
        available_plots = glob.glob("plots/*.png")
        
        # Let the agent generate PowerPoint code
        ppt_prompt = f"""
        You have completed your analysis and generated the following results:
        
        ANALYSIS RESULTS:
        {json.dumps(analysis_data, indent=2)}
        
        AVAILABLE VISUALIZATION FILES:
        {available_plots}
        
        Now use the ReportGeneratorTool to create a professional PowerPoint presentation.
        Call the report_generator tool with the analysis_results and plots parameters.
        The tool will automatically create a comprehensive PowerPoint presentation with:
        - Title slide
        - Executive summary
        - Data quality assessment
        - Visualization slides with embedded images
        - Key insights
        - Recommendations
        - Conclusion

        Simply call: report_generator(analysis_results=analysis_data, plots=available_plots)
        """
        
        print("🤖 Agent is generating PowerPoint code...")
        ppt_result = agent.run(ppt_prompt)
        print(f"🎯 PowerPoint Generation: {ppt_result}")
        
        # Verify the file was created
        if os.path.exists("analysis_report.pptx"):
            file_size = os.path.getsize("analysis_report.pptx")
            print(f"✅ PowerPoint file created successfully! Size: {file_size} bytes")
            # Clean up all PNG files in the plots directory
            for file_path in glob.glob("plots/*.png"):
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
        else:
            print("⚠️ PowerPoint file was not created")
    else:
        print("⚠️ Could not parse analysis results for PowerPoint generation")
        print(f"Debug - Final result type: {type(final_result)}")
        print(f"Debug - Final result preview: {str(final_result)[:200]}...")
        print(f"Debug - Parsed analysis_data: {analysis_data}")
except Exception as e:
    print(f"❌ Error generating PowerPoint: {e}")
    import traceback
    traceback.print_exc()
