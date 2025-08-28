# 🚀 Spark Insights

**Autonomous AI Data Scientist Assistant - Complete EDA, Visualization & ML Pipeline**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![SmolagentsAI](https://img.shields.io/badge/powered%20by-SmolagentsAI-blue.svg)](https://github.com/huggingface/smolagents)

## 📋 Overview

Spark Insights is an autonomous AI-powered data scientist that performs comprehensive Exploratory Data Analysis (EDA), generates intelligent visualizations, builds machine learning models, and creates professional PowerPoint presentations automatically. Built with SmolagentsAI framework and powered by OpenAI's advanced language models.

## ✨ Key Features

- **🤖 Autonomous Analysis**: Complete end-to-end data analysis without human intervention
- **📊 Smart Data Processing**: Automatic data loading, cleaning, and preprocessing
- **📈 Intelligent Visualizations**: Context-aware chart generation based on data characteristics
- **🧠 ML Model Building**: Automatic model selection, training, and evaluation
- **📄 PowerPoint Generation**: Professional presentation creation with embedded visualizations
- **� Comprehensive EDA**: Statistical analysis, correlation discovery, and pattern recognition
- **💡 Actionable Insights**: AI-generated recommendations and business insights
- **🎯 Interactive Interface**: Simple command-line interface for data analysis

## 🏗️ Project Structure

```
spark-insights/
├── agent.py                   # Main AI agent configuration with SmolagentsAI
├── main.py                    # Entry point and user interface
├── config.py                  # Configuration and system prompts
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (API keys)
├── tools/                     # Modular analysis tools
│   ├── __init__.py           
│   ├── file_handler.py       # Data loading and file processing
│   ├── data_analysis.py      # Statistical analysis and EDA
│   ├── visualization.py      # Chart generation with matplotlib/seaborn
│   ├── ml_model.py          # Machine learning model building
│   ├── report_generator.py   # PowerPoint presentation creation
│   └── conversation_manager.py # Chat and conversation handling
├── examples/                  # Sample datasets
│   ├── sales.csv             # Sample sales dataset
│   ├── amazon.csv            # Sample Amazon dataset
│   └── README.txt            # Dataset descriptions
├── plots/                     # Generated visualizations (auto-created)
├── artifacts/                 # ML model artifacts and outputs
├── env/                       # Python virtual environment
└── __pycache__/              # Python cache files
```

## 🧠 AI Agent Architecture

The system uses **SmolagentsAI** framework with the following tools:

- **FileHandlerTool**: Intelligent data loading for CSV/Excel files
- **DataAnalysisTool**: Comprehensive statistical analysis and EDA
- **VisualizationTool**: Context-aware chart generation
- **MLModelTool**: Automated machine learning pipeline
- **ReportGeneratorTool**: Professional PowerPoint creation
- **ConversationManagerTool**: Interactive chat capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git (for cloning)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/spark-insights.git
cd spark-insights

# Create virtual environment
python -m venv env
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
```

### Usage

```bash
# Run the AI Data Scientist
python main.py
```

The system will prompt you for a data file path and then autonomously:

1. **Load and explore** your dataset
2. **Perform comprehensive EDA** with statistical analysis
3. **Generate intelligent visualizations** based on your data
4. **Build relevant ML models** (classification/regression/clustering)
5. **Extract actionable insights** and patterns
6. **Create a PowerPoint presentation** with all findings

### Example Analysis Flow

```
🚀 Welcome to Spark Insights! Your Autonomous AI Data Scientist.

📊 This system will automatically:
   • Perform comprehensive Exploratory Data Analysis (EDA)
   • Generate dataset-specific visualizations
   • Build relevant ML models
   • Extract meaningful insights
   • Create a custom PowerPoint presentation

📁 Please provide your data file path (CSV/Excel):
> examples/sales.csv

🔄 Starting autonomous data analysis...
✅ Analysis Complete!
🎯 PowerPoint Report Created!
📄 File: analysis_report.pptx
```

## � What Spark Insights Delivers

### Automated Analysis Pipeline

1. **Data Quality Assessment**
   - Missing value analysis
   - Data type detection
   - Statistical summaries
   - Outlier identification

2. **Exploratory Data Analysis**
   - Correlation analysis
   - Distribution analysis
   - Categorical variable exploration
   - Time series analysis (if applicable)

3. **Intelligent Visualizations**
   - Histograms and distribution plots
   - Correlation heatmaps
   - Box plots and violin plots
   - Scatter plots and trend analysis
   - Bar charts for categorical data

4. **Machine Learning Pipeline**
   - Automatic problem type detection (classification/regression)
   - Feature engineering and selection
   - Model training and evaluation
   - Feature importance analysis
   - Performance metrics and confusion matrices

5. **Professional Reporting**
   - Executive summary
   - Dataset overview
   - Visualization slides with explanations
   - ML model results
   - Key insights and recommendations
   - Actionable conclusions

### Sample Output

Your analysis will generate:
- **Multiple PNG visualizations** in `plots/` directory
- **analysis_report.pptx** - Professional PowerPoint presentation
- **Model artifacts** in `artifacts/` directory
- **Console output** with step-by-step progress

## 🛠️ Technical Stack

- **AI Framework**: SmolagentsAI (Hugging Face)
- **LLM**: OpenAI GPT models
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Machine Learning**: Scikit-learn
- **Reporting**: python-pptx
- **Configuration**: python-dotenv, PyYAML

## 📖 Documentation

For detailed documentation on each component:

- [Tools Documentation](tools/README.md) - Individual tool descriptions
- [Configuration Guide](config.py) - System prompts and settings
- [Example Datasets](examples/README.txt) - Sample data descriptions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add docstrings to all functions and classes
- Test your changes with sample datasets
- Update documentation for new features

## 🚨 Requirements

```python
# Core AI and ML
smolagents>=0.1.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0

# LLM Integration
openai>=1.0.0
python-dotenv>=1.0.0

# Reporting
python-pptx>=0.6.21

# Additional utilities
requests>=2.31.0
click>=8.1.0
rich>=13.0.0
```

## � Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: OpenAI API key not found
   ```
   Solution: Ensure your `.env` file contains `OPENAI_API_KEY=your_key_here`

2. **File Not Found**
   ```
   ❌ File not found: data.csv
   ```
   Solution: Provide the full path to your data file

3. **Memory Issues with Large Files**
   ```
   MemoryError: Unable to allocate array
   ```
   Solution: Use smaller datasets or increase system memory

## �📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SmolagentsAI** by Hugging Face for the agent framework
- **OpenAI** for advanced language model capabilities
- **Python Data Science Community** for excellent libraries
- Built with modern Python best practices for autonomous data analysis 
