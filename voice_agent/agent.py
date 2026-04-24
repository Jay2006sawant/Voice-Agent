from __future__ import annotations

import json
import os
import re
from typing import Callable, Dict, Optional

from .memory import MemoryStore
from .todo_tools import TodoManager


class VoiceTodoAgent:
    """Voice-oriented assistant that manages todos and long-term memory."""

    SYSTEM_PROMPT = (
        "You are a helpful voice AI assistant. "
        "You can manage a to-do list through tools and recall important memories. "
        "Use tools when the user asks to add, update, delete, or list tasks, or asks what you remember. "
        "Keep responses concise and natural for spoken conversation."
    )

    def __init__(self) -> None:
        self.todo = TodoManager()
        self.memory = MemoryStore()
        self._tool_map: Dict[str, Callable[..., str]] = {
            "add_todo": self.todo.add_todo,
            "update_todo": self.todo.update_todo,
            "delete_todo": self.todo.delete_todo,
            "list_todos": self.todo.list_todos,
            "recall_memory": self.memory.recall,
        }

    def process(self, user_text: str) -> str:
        if not user_text.strip():
            return "I didn't catch that. Please say it again."

        self.memory.maybe_store(user_text)

        openai_response = self._process_with_openai(user_text)
        if openai_response is not None:
            return openai_response

        return self._process_rule_based(user_text)

    def _process_with_openai(self, user_text: str) -> Optional[str]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "add_todo",
                        "description": "Add a new to-do item",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                            },
                            "required": ["title"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_todo",
                        "description": "Update title or completion state of a to-do item",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "todo_id": {"type": "string"},
                                "title": {"type": "string"},
                                "done": {"type": "boolean"},
                            },
                            "required": ["todo_id"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_todo",
                        "description": "Delete a to-do item by id",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "todo_id": {"type": "string"},
                            },
                            "required": ["todo_id"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_todos",
                        "description": "List all to-do items",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "recall_memory",
                        "description": "Recall important memories; can filter by query",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                            },
                        },
                    },
                },
            ]

            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ]

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            message = response.choices[0].message

            if not message.tool_calls:
                return message.content or "Okay."

            tool_results = []
            for tool_call in message.tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments or "{}")
                tool_fn = self._tool_map.get(name)
                if tool_fn is None:
                    result = f"Tool '{name}' not available."
                else:
                    result = tool_fn(**arguments)
                tool_results.append(result)

            tool_messages = []
            for tool_call, result in zip(message.tool_calls, tool_results):
                tool_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

            follow_up = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    *messages,
                    {
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": message.tool_calls,
                    },
                    *tool_messages,
                ],
            )
            return follow_up.choices[0].message.content or "Done."
        except Exception:
            # Gracefully fallback to deterministic behavior if API fails.
            return None

    def _process_rule_based(self, user_text: str) -> str:
        text = user_text.strip()
        lower = text.lower()

        if "list" in lower and ("todo" in lower or "to-do" in lower or "task" in lower):
            return self.todo.list_todos()

        if any(token in lower for token in ("add", "create", "new task", "new todo")):
            title = self._extract_after_keywords(text, ["add", "create", "task", "todo"]) or text
            title = re.sub(r"^(a|an|to-do|todo|task)\s+", "", title, flags=re.IGNORECASE).strip()
            return self.todo.add_todo(title)

        if any(token in lower for token in ("delete", "remove")):
            todo_id = self._extract_id(text)
            if not todo_id:
                return "Please tell me the to-do id to delete."
            return self.todo.delete_todo(todo_id)

        if any(token in lower for token in ("done", "complete", "mark")):
            todo_id = self._extract_id(text)
            if not todo_id:
                return "Please tell me the to-do id to mark done."
            done_value = not ("not done" in lower or "pending" in lower)
            return self.todo.update_todo(todo_id=todo_id, done=done_value)

        if "remember" in lower or "memory" in lower or "recall" in lower:
            query = text
            for word in ["remember", "memory", "recall", "what", "do", "you", "about"]:
                query = re.sub(rf"\b{word}\b", "", query, flags=re.IGNORECASE)
            return self.memory.recall(query.strip())

        return (
            "I can help with to-dos and memory. "
            "Try: add a task, list tasks, mark one done, delete one, or ask what I remember."
        )

    @staticmethod
    def _extract_id(text: str) -> str:
        match = re.search(r"\b([a-f0-9]{8})\b", text.lower())
        return match.group(1) if match else ""

    @staticmethod
    def _extract_after_keywords(text: str, keywords: list[str]) -> str:
        lowered = text.lower()
        for keyword in keywords:
            idx = lowered.find(keyword)
            if idx != -1:
                return text[idx + len(keyword) :].strip(" :.-")
        return ""
