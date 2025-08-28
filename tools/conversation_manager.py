from smolagents import Tool
import json
import os
from datetime import datetime

class ConversationManagerTool(Tool):
    name = "conversation_manager"
    description = "Manage conversation flow: ask clarifying questions, validate user responses, save conversation context, and resume from previous sessions."
    inputs = {
        "action": {
            "type": "string",
            "description": "Action to perform (ask_question, validate_response, save_context, resume_context)"
        },
        "data": {
            "type": "object",
            "description": "Data associated with the action (question text, response to validate, context to save, etc.)"
        }
    }
    output_type = "string"

    def forward(self, action: str, data) -> str:
        """Manage conversation flow and context"""
        try:
            if action == "ask_question":
                # In a real implementation, this would prompt the user
                question = data.get("question", "Please provide more information:")
                return f"Question to user: {question}"
                
            elif action == "validate_response":
                response = data.get("response", "")
                expected_type = data.get("expected_type", "string")
                
                if expected_type == "number":
                    try:
                        float(response)
                        return "Response validated successfully"
                    except ValueError:
                        return "Invalid response: expected a number"
                elif expected_type == "file_path":
                    if os.path.exists(response):
                        return "File path validated successfully"
                    else:
                        return f"File not found: {response}"
                else:
                    return "Response validated successfully"
                
            elif action == "save_context":
                context = data.get("context", {})
                timestamp = datetime.now().isoformat()
                context_file = f"conversation_context_{timestamp}.json"
                
                with open(context_file, 'w') as f:
                    json.dump(context, f, indent=2)
                
                return f"Conversation context saved to: {context_file}"
                
            elif action == "resume_context":
                context_file = data.get("context_file", "")
                if os.path.exists(context_file):
                    with open(context_file, 'r') as f:
                        context = json.load(f)
                    return f"Context resumed from: {context_file}\n{json.dumps(context, indent=2)}"
                else:
                    return f"Context file not found: {context_file}"
            
            else:
                return f"Unknown action: {action}"
            
        except Exception as e:
            return f"Error in conversation management: {str(e)}"
