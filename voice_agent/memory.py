from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List


@dataclass
class MemoryEntry:
    timestamp: str
    content: str


class MemoryStore:
    """Simple memory module to capture and recall important user events."""

    KEYWORDS = (
        "birthday",
        "anniversary",
        "meeting",
        "exam",
        "deadline",
        "important",
        "doctor",
        "interview",
        "travel",
        "call",
    )
    QUESTION_HINTS = ("what", "when", "where", "who", "why", "how", "?")
    EXPLICIT_SAVE_HINTS = ("remember", "note", "important", "save this")

    def __init__(self, storage_path: str = "data/memory.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_memories([])

    def _read_memories(self) -> List[MemoryEntry]:
        raw = json.loads(self.storage_path.read_text(encoding="utf-8") or "[]")
        return [MemoryEntry(**item) for item in raw]

    def _write_memories(self, entries: List[MemoryEntry]) -> None:
        self.storage_path.write_text(
            json.dumps([asdict(entry) for entry in entries], indent=2),
            encoding="utf-8",
        )

    def maybe_store(self, user_text: str) -> bool:
        lower = user_text.lower()
        if any(hint in lower for hint in self.QUESTION_HINTS):
            return False

        has_keyword = any(keyword in lower for keyword in self.KEYWORDS)
        has_explicit_save_intent = any(hint in lower for hint in self.EXPLICIT_SAVE_HINTS)
        if not (has_keyword and has_explicit_save_intent):
            return False

        entries = self._read_memories()
        entries.append(
            MemoryEntry(
                timestamp=datetime.utcnow().isoformat(timespec="seconds") + "Z",
                content=user_text.strip(),
            )
        )
        self._write_memories(entries)
        return True

    def recall(self, query: str = "") -> str:
        entries = self._read_memories()
        if not entries:
            return "I don't have any important memories saved yet."

        if query.strip():
            q = query.lower()
            matches = [entry for entry in entries if q in entry.content.lower()]
        else:
            matches = entries[-5:]

        if not matches:
            return "I couldn't find a memory matching that request."

        lines = ["Here is what I remember:"]
        for entry in matches[-5:]:
            lines.append(f"- ({entry.timestamp}) {entry.content}")
        return "\n".join(lines)
