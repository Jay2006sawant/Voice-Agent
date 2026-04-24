from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional
from uuid import uuid4


@dataclass
class TodoItem:
    id: str
    title: str
    done: bool = False


class TodoManager:
    """JSON-backed CRUD toolset for to-do items."""

    def __init__(self, storage_path: str = "data/todos.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_items([])

    def _read_items(self) -> List[TodoItem]:
        if not self.storage_path.exists():
            return []
        raw = json.loads(self.storage_path.read_text(encoding="utf-8") or "[]")
        return [TodoItem(**item) for item in raw]

    def _write_items(self, items: List[TodoItem]) -> None:
        self.storage_path.write_text(
            json.dumps([asdict(item) for item in items], indent=2),
            encoding="utf-8",
        )

    def add_todo(self, title: str) -> str:
        title = title.strip()
        if not title:
            return "Cannot add an empty to-do item."

        items = self._read_items()
        todo = TodoItem(id=str(uuid4())[:8], title=title, done=False)
        items.append(todo)
        self._write_items(items)
        return f"Added to-do [{todo.id}]: {todo.title}"

    def update_todo(
        self,
        todo_id: str,
        title: Optional[str] = None,
        done: Optional[bool] = None,
    ) -> str:
        items = self._read_items()
        for item in items:
            if item.id == todo_id:
                if title is not None:
                    item.title = title.strip() or item.title
                if done is not None:
                    item.done = done
                self._write_items(items)
                status = "done" if item.done else "pending"
                return f"Updated to-do [{item.id}] -> {item.title} ({status})"
        return f"No to-do item found with id '{todo_id}'."

    def delete_todo(self, todo_id: str) -> str:
        items = self._read_items()
        remaining = [item for item in items if item.id != todo_id]
        if len(remaining) == len(items):
            return f"No to-do item found with id '{todo_id}'."
        self._write_items(remaining)
        return f"Deleted to-do item [{todo_id}]."

    def list_todos(self) -> str:
        items = self._read_items()
        if not items:
            return "Your to-do list is empty."

        lines = ["Here are your current to-dos:"]
        for item in items:
            marker = "x" if item.done else " "
            lines.append(f"- [{marker}] {item.id}: {item.title}")
        return "\n".join(lines)
