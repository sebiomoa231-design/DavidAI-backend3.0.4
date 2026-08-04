"""Conversation endpoints for David AI."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from david.conversations import append_message, count, get_conversation, list_conversations, record_conversation
from david.security.auth import get_current_user_optional
from david.security.workspace import ensure_owner, scope_user_id

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


class ConversationCreate(BaseModel):
    message: str
    reply: str
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    provider: Optional[str] = None
    task_type: Optional[str] = None


@router.get("")
async def conversations(user_id: Optional[str] = None, current_user: Optional[dict] = Depends(get_current_user_optional)):
    scoped_user_id = scope_user_id(current_user, user_id)
    return {
        "count": count(scoped_user_id),
        "items": list_conversations(user_id=scoped_user_id),
    }


@router.get("/{conversation_id}")
async def conversation_detail(conversation_id: str, current_user: Optional[dict] = Depends(get_current_user_optional)):
    convo = get_conversation(conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    ensure_owner(convo, current_user, resource_name="conversation")
    return convo


@router.post("")
async def create_conversation(payload: ConversationCreate, current_user: Optional[dict] = Depends(get_current_user_optional)):
    scoped_user_id = scope_user_id(current_user, payload.user_id)
    return record_conversation(
        message=payload.message,
        reply=payload.reply,
        user_id=scoped_user_id,
        project_id=payload.project_id,
        provider=payload.provider,
        task_type=payload.task_type,
    )


@router.post("/{conversation_id}/append")
async def append(conversation_id: str, payload: dict, current_user: Optional[dict] = Depends(get_current_user_optional)):
    convo = get_conversation(conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    ensure_owner(convo, current_user, resource_name="conversation")
    role = payload.get("role", "user")
    content = payload.get("content", "")
    updated = append_message(conversation_id, role=role, content=content)
    return updated
