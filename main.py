#!/usr/bin/env python3
"""
Automated AI Data Scientist Assistant
Performs comprehensive EDA, generates insights, visualizations, and creates PowerPoint presentation automatically
"""

import os
from agent import agent
from config import system_prompt

def main():
    # Welcome message

    [os.remove(f"plots/{f}") for f in os.listdir("plots") if f.endswith(".png")]

    print("🚀 Welcome to Spark Insights! Your Autonomous AI Data Scientist.\n")
    print("📊 This system will automatically:")
    print("   • Perform comprehensive Exploratory Data Analysis (EDA)")
    print("   • Generate dataset-specific visualizations")
    print("   • Build relevant ML models")
    print("   • Extract meaningful insights")
    print("   • Create a custom PowerPoint presentation")
    print()

    # Get data file path
    data_path = input("📁 Please provide your data file path (CSV/Excel):\n> ").strip()
    
    if not os.path.exists(data_path):
        print(f"❌ File not found: {data_path}")
        return

    # Run complete automated analysis with PowerPoint generation
    print("\n🔄 Starting autonomous data analysis...")
    
    full_prompt = f"""{system_prompt}

**DATA FILE:** {data_path}

**YOUR MISSION:**
1. Load and analyze this specific dataset
2. Perform comprehensive EDA based on what you find
3. Generate appropriate visualizations for THIS data
4. Build relevant ML models for THIS dataset  
5. Extract insights specific to THIS analysis
6. Write custom Python code to create a PowerPoint presentation that tells the story of YOUR findings

**POWERPOINT GENERATION:**
After completing your analysis, write Python code using python-pptx to create 'analysis_report.pptx' with:
- Title slide with your analysis title
- Overview of the dataset you analyzed
- Slides for each visualization you created (with explanations)
- Key insights you discovered
- Recommendations based on your findings
- Professional formatting

Make everything specific to your actual analysis results, not generic templates."""

    try:
        final_result = agent.run(full_prompt)
        print(f"\n✅ Analysis Complete!")
        print(f"📊 Results: {final_result}")
        
        # Check if PowerPoint was created
        if os.path.exists("analysis_report.pptx"):
            file_size = os.path.getsize("analysis_report.pptx")
            print(f"\n🎯 PowerPoint Report Created!")
            print(f"📄 File: analysis_report.pptx ({file_size} bytes)")
        else:
            print("\n⚠️ PowerPoint file not found. The agent may need to run the PowerPoint generation code.")
            
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
