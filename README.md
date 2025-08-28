# 🚀 Spark-Insight

**AI-powered data analysis tool with conversational interface**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/your-repo/spark-insight)

## 📋 Overview

Spark-Insight is an advanced AI-powered data analysis tool that transforms raw data into actionable business insights. Built with a modular architecture, it provides a conversational interface for data exploration, statistical analysis, and automated report generation.

## ✨ Key Features

- **🤖 Multi-LLM Support**: OpenAI and Ollama integration
- **📊 Data Processing**: Support for CSV, Excel, JSON, and Parquet files
- **🧹 Automated Cleaning**: Intelligent data preprocessing and quality checks
- **📈 Smart Analysis**: AI-driven statistical analysis and insights generation
- **📄 PPT Reports**: Generate reports in PPTX format
- **💾 Session Management**: Save and load analysis sessions
- **⚙️ Configurable**: Flexible configuration via environment variables and YAML
- **🎯 Interactive CLI**: Rich, user-friendly command-line interface

## 🏗️ Project Structure

```
src/
├── core/                    # Core functionality
│   ├── config.py           # Configuration management
│   ├── exceptions.py       # Custom exceptions
│   └── base.py            # Base classes and interfaces
├── data/                   # Data handling
│   ├── loaders/           # Data loading strategies
│   ├── processors/        # Data processing pipelines
│   └── validators/        # Data validation
├── analysis/              # Analysis components
│   ├── engines/           # Analysis engines
│   ├── prompts/           # Prompt management
│   └── interpreters/      # Result interpretation
├── reporting/             # Report generation
│   ├── formatters/        # Output formatters
│   ├── templates/         # Report templates
│   └── exporters/         # Export strategies
├── llm/                   # LLM integration
│   ├── base.py           # Base LLM client
│   ├── openai_client.py  # OpenAI integration
│   └── ollama_client.py  # Ollama integration
└── cli/                   # Command-line interface
    ├── commands/          # CLI commands
    └── interfaces/        # User interfaces
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/spark-insight.git
cd spark-insight

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Basic Usage

```bash
# Interactive mode
spark-insight interactive

# Direct file analysis
spark-insight analyze --file data.csv --goal "Analyze sales trends"

# Show configuration
spark-insight config

# Show info
spark-insight info
```

### Configuration

Create a `.env` file in your project root:

```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-4
LLM_API_KEY=your_openai_api_key
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000

# Data Configuration
DATA_MAX_FILE_SIZE=100
DATA_CHUNK_SIZE=10000
DATA_DEFAULT_ENCODING=utf-8

# Reporting Configuration
REPORTING_OUTPUT_FORMAT=pptx
REPORTING_OUTPUT_DIR=reports
REPORTING_TEMPLATE_DIR=templates
```

## 📖 Documentation

For detailed documentation, see [README_ENHANCED.md](README_ENHANCED.md).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python best practices
- Powered by OpenAI and Ollama
- Inspired by the need for accessible AI-powered data analysis 