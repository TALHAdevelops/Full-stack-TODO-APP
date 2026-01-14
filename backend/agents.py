"""OpenAI Agent SDK wrapper for TaskFlow chatbot

@spec: T-321 to T-322 (spec.md §Agent Behavior, plan.md §Agent Architecture)
"""

import logging
import json
import os
from typing import Optional, Literal
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from mcp_server import invoke_tool, MCP_TOOLS

# Load .env file
ENV_FILE = Path(__file__).resolve().parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI client not installed. Install with: pip install openai")

# Initialize OpenAI client
openai_client = None
if OPENAI_AVAILABLE:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        openai_client = OpenAI(api_key=api_key)
    else:
        logger.warning("OPENAI_API_KEY not set. Agent will use fallback responses.")


# System prompt for the agent
SYSTEM_PROMPT = """You are a helpful task management assistant. Your job is to help users manage their todo list.

You have access to the following operations:
- add_task: Create a new task
- list_tasks: Show pending or completed tasks
- complete_task: Mark a task as done
- delete_task: Remove a task
- update_task: Modify a task

Always:
1. Understand the user's intent from natural language
2. Invoke the appropriate tool(s)
3. Confirm the action with a friendly response
4. Include the task ID or details for reference
5. Ask for clarification if the request is ambiguous

Natural language variations you should recognize:
- "Add/create/remember/make" → add_task
- "Show/list/pending/what" → list_tasks
- "Done/complete/finished/mark" → complete_task
- "Delete/remove/get rid" → delete_task (ask for confirmation)
- "Change/update/rename/modify" → update_task

For ambiguous requests, ask clarifying questions rather than guessing.
For destructive operations (delete), always ask for confirmation first."""


def parse_intent(message: str) -> str:
    """
    Extract user intent from message.

    Returns: One of GREETING, CREATE, LIST, COMPLETE, UPDATE, DELETE, CLARIFY

    @spec: T-322 (spec.md FR-318-FR-326)
    """
    message_lower = message.lower().strip()

    # GREETING intent
    if any(word in message_lower for word in ["hello", "hi", "hey", "assalam o alaikum", "salam", "greetings", "good morning", "good afternoon", "good evening"]):
        return "GREETING"

    # CREATE intent
    if any(word in message_lower for word in ["add", "create", "remember", "make", "new task"]):
        return "CREATE"

    # LIST intent
    if any(word in message_lower for word in ["show", "list", "pending", "what", "view", "display"]):
        return "LIST"

    # COMPLETE intent
    if any(word in message_lower for word in ["done", "complete", "finished", "mark"]):
        return "COMPLETE"

    # DELETE intent
    if any(word in message_lower for word in ["delete", "remove", "get rid"]):
        return "DELETE"

    # UPDATE intent
    if any(word in message_lower for word in ["change", "update", "rename", "modify"]):
        return "UPDATE"

    # Default to clarify for ambiguous intent
    return "CLARIFY"


def select_tools(intent: str) -> list:
    """
    Determine which MCP tools to invoke based on intent.

    @spec: T-322 (spec.md FR-339)
    """
    intent_to_tools = {
        "GREETING": [],
        "CREATE": ["add_task"],
        "LIST": ["list_tasks"],
        "COMPLETE": ["complete_task"],
        "UPDATE": ["update_task"],
        "DELETE": ["delete_task"],
        "CLARIFY": []
    }

    return intent_to_tools.get(intent, [])


def format_tool_calls(tool_calls: list) -> str:
    """Format tool calls for inclusion in response"""
    if not tool_calls:
        return ""

    formatted = "\n\n**Actions taken:**"
    for call in tool_calls:
        tool_name = call.get("tool_name", "unknown")
        result = call.get("result", {})

        if result.get("status") == "success":
            data = result.get("data", {})
            if tool_name == "add_task":
                formatted += f"\n✓ Created task: {data.get('title')} (ID: {data.get('task_id')})"
            elif tool_name == "list_tasks":
                count = len(data)
                formatted += f"\n✓ Found {count} tasks"
            elif tool_name == "complete_task":
                formatted += f"\n✓ Marked task {data.get('task_id')} as complete"
            elif tool_name == "update_task":
                formatted += f"\n✓ Updated task {data.get('task_id')}"
            elif tool_name == "delete_task":
                formatted += f"\n✓ Deleted task {data.get('task_id')}"
        else:
            error = result.get("error", "Unknown error")
            formatted += f"\n✗ {tool_name} failed: {error}"

    return formatted


class Agent:
    """OpenAI Agent wrapper for task management"""

    def __init__(self, user_id: str):
        """Initialize agent for a specific user"""
        self.user_id = user_id
        self.tools = MCP_TOOLS
        self.system_prompt = SYSTEM_PROMPT

    def run(self, messages: list, user_message: str) -> dict:
        """
        Run agent on user message and return response.

        Args:
            messages: Conversation history [{role, content}, ...]
            user_message: Current user message

        Returns:
            {content, tool_calls}

        @spec: T-321 (spec.md FR-318-FR-326)
        """
        try:
            # Parse user intent
            intent = parse_intent(user_message)
            logger.info(f"Agent: user={self.user_id}, intent={intent}, message={user_message[:50]}")

            # Handle greeting intent
            if intent == "GREETING":
                menu_text = ("Nice to meet you! 👋 Here's what I can help you with:\n\n"
                           "📝 **Add tasks**: 'Add [task]'\n"
                           "📋 **View tasks**: 'Show pending tasks'\n"
                           "✅ **Complete tasks**: 'Mark task [id] done'\n"
                           "✏️ **Update tasks**: 'Update task [id] to [new description]'\n"
                           "🗑️ **Delete tasks**: 'Delete task [id]'\n\n"
                           "What would you like to do?")
                return {
                    "content": menu_text,
                    "tool_calls": []
                }

            # Handle clarification intent
            if intent == "CLARIFY":
                return {
                    "content": "I'm not sure what you'd like to do. Could you clarify? For example:\n"
                              "- 'Add [task name]' to create a task\n"
                              "- 'Show pending tasks' to list tasks\n"
                              "- 'Mark task [id] done' to complete a task\n"
                              "- 'Delete task [id]' to remove a task\n"
                              "- 'Update task [id] to [new description]' to modify a task",
                    "tool_calls": []
                }

            # Select tools for intent
            selected_tools = select_tools(intent)

            if not selected_tools:
                return {
                    "content": "I couldn't determine what action to take. Please be more specific.",
                    "tool_calls": []
                }

            # Invoke tools
            tool_calls = []
            responses = []

            logger.info(f"Selected tools for intent {intent}: {selected_tools}")
            
            for tool_name in selected_tools:
                # Parse message for tool parameters
                logger.info(f"Invoking tool: {tool_name} for message: {user_message}")
                tool_result, tool_input = self._invoke_tool_for_intent(intent, tool_name, user_message)
                logger.info(f"Tool result for {tool_name}: {tool_result}")
                tool_calls.append({
                    "tool_name": tool_name,
                    "input": tool_input,
                    "result": tool_result
                })
                responses.append(tool_result)

            # Generate response based on tool results
            response_content = self._generate_response(intent, responses, user_message, tool_calls)

            return {
                "content": response_content,
                "tool_calls": tool_calls
            }

        except Exception as e:
            logger.error(f"Agent error: {str(e)}", exc_info=True)
            return {
                "content": "Sorry, I encountered an error processing your request. Please try again.",
                "tool_calls": []
            }

    def _invoke_tool_for_intent(self, intent: str, tool_name: str, user_message: str) -> tuple:
        """Invoke tool with parameters extracted from user message. Returns (result, input)"""
        try:
            tool_input = {}
            
            if intent == "CREATE":
                # Extract task title from message
                # Simple heuristic: remove common prefixes and use the rest
                title = user_message.lower()
                for prefix in ["add", "create", "remember", "make", "new task"]:
                    if title.startswith(prefix):
                        title = title[len(prefix):].strip()
                        break

                title = title.strip('.:;!?')
                if not title:
                    return (
                        {
                            "status": "error",
                            "error": "Please provide a task title",
                            "code": "INVALID_INPUT"
                        },
                        tool_input
                    )

                logger.info(f"Extracted title from '{user_message}': '{title}'")
                tool_input = {"user_id": self.user_id, "title": title}
                result = invoke_tool(tool_name, **tool_input)
                return (result, tool_input)

            elif intent == "LIST":
                # Determine filter from message
                filter_type = None
                if "completed" in user_message.lower():
                    filter_type = "completed"
                elif "pending" in user_message.lower():
                    filter_type = "pending"

                tool_input = {"user_id": self.user_id, "filter": filter_type}
                result = invoke_tool(tool_name, **tool_input)
                return (result, tool_input)

            elif intent == "COMPLETE":
                # Extract task ID from message
                task_id = self._extract_task_id(user_message)
                if not task_id:
                    return (
                        {
                            "status": "error",
                            "error": "Please specify which task to complete (by ID or name)",
                            "code": "INVALID_INPUT"
                        },
                        tool_input
                    )

                tool_input = {"user_id": self.user_id, "task_id": task_id}
                result = invoke_tool(tool_name, **tool_input)
                return (result, tool_input)

            elif intent == "UPDATE":
                # Extract task ID and new title
                task_id = self._extract_task_id(user_message)
                if not task_id:
                    return (
                        {
                            "status": "error",
                            "error": "Please specify which task to update (by ID)",
                            "code": "INVALID_INPUT"
                        },
                        tool_input
                    )

                # Extract new title after "to" keyword
                new_title = None
                if " to " in user_message.lower():
                    parts = user_message.lower().split(" to ", 1)
                    if len(parts) > 1:
                        new_title = parts[1].strip('":; ')

                if not new_title:
                    return (
                        {
                            "status": "error",
                            "error": "Please specify the new task description",
                            "code": "INVALID_INPUT"
                        },
                        tool_input
                    )

                tool_input = {"user_id": self.user_id, "task_id": task_id, "title": new_title}
                result = invoke_tool(tool_name, **tool_input)
                return (result, tool_input)

            elif intent == "DELETE":
                # Extract task ID
                task_id = self._extract_task_id(user_message)
                if not task_id:
                    return (
                        {
                            "status": "error",
                            "error": "Please specify which task to delete (by ID)",
                            "code": "INVALID_INPUT"
                        },
                        tool_input
                    )

                tool_input = {"user_id": self.user_id, "task_id": task_id}
                result = invoke_tool(tool_name, **tool_input)
                return (result, tool_input)

            else:
                return (
                    {
                        "status": "error",
                        "error": "Unknown intent",
                        "code": "INVALID_INTENT"
                    },
                    tool_input
                )

        except Exception as e:
            logger.error(f"Tool invocation error: {str(e)}", exc_info=True)
            return (
                {
                    "status": "error",
                    "error": "Failed to execute tool",
                    "code": "TOOL_ERROR"
                },
                {}
            )

    def _extract_task_id(self, message: str) -> Optional[int]:
        """Extract task ID from message (simple number extraction)"""
        import re
        # Look for "task X" or just a number
        match = re.search(r'task\s+(\d+)', message.lower())
        if match:
            return int(match.group(1))

        # Try to find standalone number
        numbers = re.findall(r'\b(\d+)\b', message)
        if numbers:
            return int(numbers[0])

        return None

    def _generate_response(self, intent: str, responses: list, user_message: str, tool_calls: list) -> str:
        """Generate natural language response based on tool results"""
        if not responses:
            return "I couldn't process your request. Please try again."

        first_response = responses[0]

        if first_response.get("status") == "error":
            error = first_response.get("error", "Unknown error")
            return f"I encountered an issue: {error}. Could you provide more details?"

        data = first_response.get("data", {})

        # Generate response based on intent and data
        if intent == "CREATE":
            title = data.get("title", "your task")
            task_id = data.get("task_id", "")
            response = f"✓ I've created the task '{title}' for you (ID: {task_id})"

        elif intent == "LIST":
            tasks = data
            if not tasks:
                response = "You don't have any tasks right now. Great job!"
            else:
                response = "Here are your tasks:\n"
                for task in tasks:
                    status = "✓" if task.get("completed") else "○"
                    response += f"\n{status} Task {task.get('id')}: {task.get('title')}"

        elif intent == "COMPLETE":
            task_id = data.get("task_id", "")
            response = f"✓ I've marked task {task_id} as complete. Nice work!"

        elif intent == "UPDATE":
            task_id = data.get("task_id", "")
            title = data.get("title", "")
            response = f"✓ I've updated task {task_id} to '{title}'"

        elif intent == "DELETE":
            task_id = data.get("task_id", "")
            response = f"✓ I've permanently deleted task {task_id}"

        else:
            response = "Done!"

        # Append tool calls info for transparency
        response += format_tool_calls(tool_calls)

        return response


def create_agent(user_id: str) -> Agent:
    """Factory function to create an agent for a user"""
    return Agent(user_id)
