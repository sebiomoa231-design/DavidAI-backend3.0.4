"""Conversation persistence for David AI."""
from __future__ import annotations

from typing import Optional

from david.database.json_store import JSONStore
from david.utils.helpers import new_id, now_iso, clip_text

store = JSONStore("conversations")


def record_conversation(
    message: str,
    reply: str,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    provider: Optional[str] = None,
    task_type: Optional[str] = None,
) -> dict:
    entry = {
        "id": new_id("conv"),
        "user_id": user_id,
        "project_id": project_id,
        "provider": provider,
        "task_type": task_type,
        "title": clip_text(message, 80),
        "messages": [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ],
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    store.add(entry)
    return entry


def list_conversations(user_id: Optional[str] = None) -> list[dict]:
    if user_id is None:
        return store.all()
    return store.find(lambda c: c.get("user_id") == user_id)


def get_conversation(conversation_id: str) -> Optional[dict]:
    return store.get(conversation_id)


def count(user_id: Optional[str] = None) -> int:
    return len(list_conversations(user_id))


def append_message(conversation_id: str, role: str, content: str) -> Optional[dict]:
    convo = store.get(conversation_id)
    if convo is None:
        return None
    messages = convo.get("messages", [])
    messages.append({"role": role, "content": content})
    return store.update(conversation_id, {"messages": messages, "updated_at": now_iso()})
