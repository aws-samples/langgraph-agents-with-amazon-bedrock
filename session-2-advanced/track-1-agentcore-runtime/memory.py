"""Optional AgentCore Memory wiring for the LangGraph agent (framework-agnostic).

We use `bedrock_agentcore.memory.MemorySessionManager` directly rather than the
Strands-only integration helper, so it works with LangGraph. Everything here is a
no-op until `AGENTCORE_MEMORY_ID` is set, which lets the agent deploy first with
NO_MEMORY and adopt memory afterwards (see the lab README, Step 3).

After `agentcore add memory --name <NAME> --strategies SEMANTIC` + `agentcore
deploy`, AgentCore injects an env var `MEMORY_<NAME>_ID` into the runtime. Point
`AGENTCORE_MEMORY_ID` at that value.

API note: method/import names below match the current AgentCore docs; confirm
against your installed `bedrock-agentcore` version during the pre-flight.
"""

import os

REGION = os.getenv("AWS_REGION", "us-east-1")
MEMORY_ID = os.getenv("AGENTCORE_MEMORY_ID")  # = your MEMORY_<NAME>_ID value

_manager_singleton = None


def _manager():
    """Lazily build a MemorySessionManager, or None if memory isn't configured."""
    global _manager_singleton
    if not MEMORY_ID:
        return None
    if _manager_singleton is None:
        from bedrock_agentcore.memory import MemorySessionManager

        _manager_singleton = MemorySessionManager(
            memory_id=MEMORY_ID, region_name=REGION
        )
    return _manager_singleton


def load_context(actor_id, session_id, query, top_k=3):
    """Return relevant long-term memories as a string, or '' when disabled."""
    mgr = _manager()
    if not mgr:
        return ""
    try:
        session = mgr.create_memory_session(actor_id=actor_id, session_id=session_id)
        records = session.search_long_term_memories(
            query=query, namespace_path="/", top_k=top_k
        )
        return "\n".join(str(r) for r in records)
    except Exception:
        # Memory is an enhancement, never a hard dependency for answering.
        return ""


def save_turns(actor_id, session_id, user_text, assistant_text):
    """Persist a user/assistant turn pair to short-term + long-term memory."""
    mgr = _manager()
    if not mgr:
        return
    try:
        from bedrock_agentcore.memory.constants import (
            ConversationalMessage,
            MessageRole,
        )

        session = mgr.create_memory_session(actor_id=actor_id, session_id=session_id)
        session.add_turns(
            messages=[ConversationalMessage(user_text, MessageRole.USER)]
        )
        session.add_turns(
            messages=[ConversationalMessage(assistant_text, MessageRole.ASSISTANT)]
        )
    except Exception:
        return
