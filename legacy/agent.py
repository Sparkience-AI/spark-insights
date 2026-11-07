from smolagents import CodeAgent, DuckDuckGoSearchTool, PythonInterpreterTool, WikipediaSearchTool
from config import model, additional_authorized_imports
from tools.file_handler import FileHandlerTool
from tools.data_analysis import DataAnalysisTool
from tools.ml_model import MLModelTool
from tools.visualization import VisualizationTool
from tools.report_generator import ReportGeneratorTool
from tools.conversation_manager import ConversationManagerTool

# Configure agent with all tools
agent = CodeAgent(
    tools=[
        DuckDuckGoSearchTool(),
        PythonInterpreterTool(),
        WikipediaSearchTool(),
        FileHandlerTool(),
        DataAnalysisTool(),
        MLModelTool(),
        VisualizationTool(),
        ReportGeneratorTool(),
        ConversationManagerTool(),
    ],
    model=model,
    additional_authorized_imports=additional_authorized_imports
)