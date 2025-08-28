# 🚀 Spark-Insight

**AI-powered data analysis tool with conversational interface**

---

⚠️ **Important:** This project depends on the `smolagents` Python package, which is not available on PyPI or in this repository. You must provide or install this package for the code to run. If you do not have access to `smolagents`, the main features will not work.

---

## 📋 Overview

Spark-Insight is an advanced AI-powered data analysis tool that transforms raw data into actionable business insights. Built with a modular architecture, it provides a conversational interface for data exploration, statistical analysis, and automated report generation.

## 🏗️ Project Structure

```
SparkInsights/
├── agent.py
├── code_agent.py
├── config.py
├── main.py
├── requirements.txt
├── README.md
├── tools/
│   ├── conversation_manager.py
│   ├── data_analysis.py
│   ├── file_handler.py
│   ├── ml_model.py
│   ├── report_generator.py
│   ├── visualization.py
├── examples/
├── models/
├── plots/
├── results/
└── venv/
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
# 
git clone https://github.com/Sparkience-AI/spark-insights
cd spark-insight

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Run the main application
python3 main.py
```
