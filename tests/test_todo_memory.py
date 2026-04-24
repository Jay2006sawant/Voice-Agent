from voice_agent.memory import MemoryStore
from voice_agent.todo_tools import TodoManager


def test_todo_crud(tmp_path):
    todo = TodoManager(storage_path=str(tmp_path / "todos.json"))

    added = todo.add_todo("Buy milk")
    assert "Added to-do" in added

    listing = todo.list_todos()
    assert "Buy milk" in listing

    todo_id = listing.split("\n")[1].split()[2].replace(":", "")
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
