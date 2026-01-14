"""MCP Server implementation for TaskFlow chat - exposes task management tools

@spec: T-306 to T-311 (spec.md §MCP Tools, plan.md §MCP Server)
"""

import json
import logging
from typing import Optional, Literal
from datetime import datetime
from sqlmodel import Session, select
from models import Task
from db import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPToolError(Exception):
    """Base exception for MCP tool errors"""
    pass


class ValidationError(MCPToolError):
    """Input validation error"""
    pass


class NotFoundError(MCPToolError):
    """Resource not found error"""
    pass


class UnauthorizedError(MCPToolError):
    """User isolation violation"""
    pass


def _validate_user_id(user_id: str) -> None:
    """Validate user_id format (non-empty, reasonable length)"""
    if not user_id or len(user_id) > 255 or not isinstance(user_id, str):
        raise ValidationError("Invalid user_id: must be non-empty string ≤255 chars")


def _validate_task_id(task_id: int) -> None:
    """Validate task_id format"""
    if not isinstance(task_id, int) or task_id <= 0:
        raise ValidationError("Invalid task_id: must be positive integer")


def _validate_title(title: str) -> str:
    """Validate and normalize title"""
    if not isinstance(title, str):
        raise ValidationError("Title must be a string")

    title = title.strip()
    if not title or len(title) > 200:
        raise ValidationError("Title must be 1-200 characters")

    return title


def _validate_description(description: Optional[str]) -> Optional[str]:
    """Validate and normalize description"""
    if description is None:
        return None

    if not isinstance(description, str):
        raise ValidationError("Description must be a string")

    description = description.strip()
    if len(description) > 1000:
        raise ValidationError("Description max 1000 characters")

    return description if description else None


def _verify_task_ownership(session: Session, user_id: str, task_id: int) -> Task:
    """Verify user owns the task, return task or raise error"""
    _validate_user_id(user_id)
    _validate_task_id(task_id)

    task = session.get(Task, task_id)
    if not task:
        raise NotFoundError(f"Task {task_id} not found")

    if task.user_id != user_id:
        raise UnauthorizedError(f"User {user_id} does not own task {task_id}")

    return task


# ===== MCP Tools Implementation =====

def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> dict:
    """
    Create a new task for a user.

    Args:
        user_id: UUID of the user creating the task
        title: Task title (1-200 characters)
        description: Optional task description (0-1000 characters)

    Returns:
        {task_id, user_id, title, created_at}

    Raises:
        ValidationError: If inputs invalid

    @spec: T-307 (spec.md FR-327)
    """
    try:
        _validate_user_id(user_id)
        title = _validate_title(title)
        description = _validate_description(description)

        with Session(engine) as session:
            # Verify user exists
            from models import User
            user = session.get(User, user_id)
            if not user:
                raise ValidationError(f"User {user_id} not found. Please log in again.")
            
            new_task = Task(
                user_id=user_id,
                title=title,
                description=description or ""
            )
            session.add(new_task)
            session.commit()
            session.refresh(new_task)

            logger.info(f"add_task: user={user_id}, task_id={new_task.id}, title={title}")

            return {
                "task_id": new_task.id,
                "user_id": user_id,
                "title": title,
                "created_at": new_task.created_at.isoformat()
            }
    except MCPToolError:
        raise
    except Exception as e:
        logger.error(f"add_task error: {str(e)}", exc_info=True)
        raise MCPToolError(f"Failed to create task: {str(e)}")


def list_tasks(
    user_id: str,
    filter: Optional[Literal["pending", "completed"]] = None
) -> list:
    """
    Retrieve user's tasks with optional filtering.

    Args:
        user_id: UUID of the user
        filter: Optional filter - "pending" or "completed"

    Returns:
        list[{id, title, completed, created_at}]

    Raises:
        ValidationError: If inputs invalid

    @spec: T-308 (spec.md FR-328)
    """
    try:
        _validate_user_id(user_id)

        if filter and filter not in ["pending", "completed"]:
            raise ValidationError(f"Invalid filter: {filter}. Use 'pending', 'completed', or None")

        with Session(engine) as session:
            statement = select(Task).where(Task.user_id == user_id)

            if filter == "pending":
                statement = statement.where(Task.completed == False)
            elif filter == "completed":
                statement = statement.where(Task.completed == True)

            statement = statement.order_by(Task.created_at.desc())
            tasks = session.exec(statement).all()

            logger.info(f"list_tasks: user={user_id}, filter={filter}, count={len(tasks)}")

            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ]
    except MCPToolError:
        raise
    except Exception as e:
        logger.error(f"list_tasks error: {str(e)}")
        raise MCPToolError(f"Failed to list tasks: {str(e)}")


def complete_task(user_id: str, task_id: int) -> dict:
    """
    Mark a task as completed.

    Args:
        user_id: UUID of the user
        task_id: ID of the task to complete

    Returns:
        {task_id, status, completed_at}

    Raises:
        NotFoundError: If task not found
        UnauthorizedError: If user doesn't own task
        ValidationError: If already completed

    @spec: T-309 (spec.md FR-329)
    """
    try:
        with Session(engine) as session:
            task = _verify_task_ownership(session, user_id, task_id)

            if task.completed:
                raise ValidationError(f"Task {task_id} is already completed")

            task.completed = True
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

            logger.info(f"complete_task: user={user_id}, task_id={task_id}")

            return {
                "task_id": task.id,
                "status": "completed",
                "completed_at": task.updated_at.isoformat()
            }
    except MCPToolError:
        raise
    except Exception as e:
        logger.error(f"complete_task error: {str(e)}")
        raise MCPToolError(f"Failed to complete task: {str(e)}")


def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """
    Update task title or description.

    Args:
        user_id: UUID of the user
        task_id: ID of the task to update
        title: Optional new title (1-200 characters)
        description: Optional new description (0-1000 characters)

    Returns:
        {task_id, title, description, updated_at}

    Raises:
        NotFoundError: If task not found
        UnauthorizedError: If user doesn't own task
        ValidationError: If inputs invalid or no fields provided

    @spec: T-310 (spec.md FR-331)
    """
    try:
        if title is None and description is None:
            raise ValidationError("Must provide at least one of: title, description")

        with Session(engine) as session:
            task = _verify_task_ownership(session, user_id, task_id)

            if title is not None:
                task.title = _validate_title(title)

            if description is not None:
                task.description = _validate_description(description) or ""

            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

            logger.info(f"update_task: user={user_id}, task_id={task_id}")

            return {
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "updated_at": task.updated_at.isoformat()
            }
    except MCPToolError:
        raise
    except Exception as e:
        logger.error(f"update_task error: {str(e)}")
        raise MCPToolError(f"Failed to update task: {str(e)}")


def delete_task(user_id: str, task_id: int) -> dict:
    """
    Permanently delete a task.

    Args:
        user_id: UUID of the user
        task_id: ID of the task to delete

    Returns:
        {task_id, status, deleted_at}

    Raises:
        NotFoundError: If task not found
        UnauthorizedError: If user doesn't own task

    @spec: T-311 (spec.md FR-330)
    """
    try:
        with Session(engine) as session:
            task = _verify_task_ownership(session, user_id, task_id)

            task_id_deleted = task.id
            session.delete(task)
            session.commit()

            logger.info(f"delete_task: user={user_id}, task_id={task_id}")

            return {
                "task_id": task_id_deleted,
                "status": "deleted",
                "deleted_at": datetime.utcnow().isoformat()
            }
    except MCPToolError:
        raise
    except Exception as e:
        logger.error(f"delete_task error: {str(e)}")
        raise MCPToolError(f"Failed to delete task: {str(e)}")


# ===== MCP Tool Registry =====

MCP_TOOLS = {
    "add_task": {
        "name": "add_task",
        "description": "Create a new task for the user",
        "function": add_task,
        "parameters": {
            "user_id": {"type": "string", "description": "User ID"},
            "title": {"type": "string", "description": "Task title (1-200 chars)"},
            "description": {"type": "string", "description": "Optional task description (0-1000 chars)"}
        }
    },
    "list_tasks": {
        "name": "list_tasks",
        "description": "Retrieve user's tasks with optional filtering",
        "function": list_tasks,
        "parameters": {
            "user_id": {"type": "string", "description": "User ID"},
            "filter": {"type": "string", "enum": ["pending", "completed"], "description": "Optional filter"}
        }
    },
    "complete_task": {
        "name": "complete_task",
        "description": "Mark a task as completed",
        "function": complete_task,
        "parameters": {
            "user_id": {"type": "string", "description": "User ID"},
            "task_id": {"type": "integer", "description": "Task ID"}
        }
    },
    "update_task": {
        "name": "update_task",
        "description": "Update task title or description",
        "function": update_task,
        "parameters": {
            "user_id": {"type": "string", "description": "User ID"},
            "task_id": {"type": "integer", "description": "Task ID"},
            "title": {"type": "string", "description": "Optional new title"},
            "description": {"type": "string", "description": "Optional new description"}
        }
    },
    "delete_task": {
        "name": "delete_task",
        "description": "Permanently delete a task",
        "function": delete_task,
        "parameters": {
            "user_id": {"type": "string", "description": "User ID"},
            "task_id": {"type": "integer", "description": "Task ID"}
        }
    }
}


def invoke_tool(tool_name: str, **kwargs) -> dict:
    """
    Invoke an MCP tool and return result or error.

    Args:
        tool_name: Name of the tool to invoke
        **kwargs: Tool parameters

    Returns:
        {status, data} or {status, error, code}
    """
    logger.info(f"invoke_tool called: {tool_name} with kwargs: {kwargs}")
    
    if tool_name not in MCP_TOOLS:
        logger.error(f"Unknown tool: {tool_name}")
        return {
            "status": "error",
            "error": f"Unknown tool: {tool_name}",
            "code": "UNKNOWN_TOOL"
        }

    try:
        tool_func = MCP_TOOLS[tool_name]["function"]
        logger.info(f"Executing tool function: {tool_func.__name__}")
        result = tool_func(**kwargs)
        logger.info(f"Tool {tool_name} returned: {result}")

        return {
            "status": "success",
            "data": result
        }
    except ValidationError as e:
        logger.warning(f"Validation error in {tool_name}: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "code": "VALIDATION_ERROR"
        }
    except NotFoundError as e:
        logger.warning(f"Not found error in {tool_name}: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "code": "NOT_FOUND"
        }
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized error in {tool_name}: {str(e)}")
        return {
            "status": "error",
            "error": "Unauthorized",
            "code": "UNAUTHORIZED"
        }
    except MCPToolError as e:
        logger.error(f"MCP tool error in {tool_name}: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": "Tool execution failed",
            "code": "TOOL_ERROR"
        }
    except Exception as e:
        logger.error(f"Unexpected error in {tool_name}: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }
