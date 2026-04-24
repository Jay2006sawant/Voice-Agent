import re

from voice_agent.agent import VoiceTodoAgent
from voice_agent.memory import MemoryStore
from voice_agent.todo_tools import TodoManager


def test_todo_crud(tmp_path):
    todo = TodoManager(storage_path=str(tmp_path / "todos.json"))

    added = todo.add_todo("Buy milk")
    assert "Added to-do" in added

    listing = todo.list_todos()
    assert "Buy milk" in listing

    todo_id = re.search(r"\b([a-f0-9]{8})\b", listing.lower()).group(1)
    updated = todo.update_todo(todo_id, done=True)
    assert "done" in updated

    deleted = todo.delete_todo(todo_id)
    assert "Deleted" in deleted


def test_memory_store(tmp_path):
    memory = MemoryStore(storage_path=str(tmp_path / "memory.json"))

    stored = memory.maybe_store("My interview is on Monday, this is important")
    assert stored is True

    recall = memory.recall("interview")
    assert "interview" in recall.lower()


def test_memory_does_not_store_questions(tmp_path):
    memory = MemoryStore(storage_path=str(tmp_path / "memory.json"))
    assert memory.maybe_store("What do you remember about my interview?") is False


def test_agent_rule_based_todo_flow(tmp_path):
    agent = VoiceTodoAgent()
    agent.todo = TodoManager(storage_path=str(tmp_path / "todos.json"))
    agent.memory = MemoryStore(storage_path=str(tmp_path / "memory.json"))

    add_out = agent.process("add task buy groceries")
    assert "Added to-do" in add_out

    list_out = agent.process("list todos")
    assert "buy groceries" in list_out.lower()
    todo_id = re.search(r"\b([a-f0-9]{8})\b", list_out.lower()).group(1)

    done_out = agent.process(f"mark {todo_id} done")
    assert "updated to-do" in done_out.lower()
    assert "done" in done_out.lower()

    del_out = agent.process(f"delete {todo_id}")
    assert "deleted to-do item" in del_out.lower()
