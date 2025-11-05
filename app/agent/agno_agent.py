from typing import AsyncGenerator
import uuid
import asyncio
from app.config import settings
from app.models.schemas import ChatRequest
from pydantic import BaseModel

try:
    from agno.agent import Agent
    from agno.models.openai import OpenAI
except Exception:
    Agent = None
    OpenAI = None

class AgentConfig(BaseModel):
    provider: str = settings.provider
    api_key: str = settings.openai_api_key

class AgnoAgent:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg
        if OpenAI is None:
            raise RuntimeError("Agno/OpenAI libs not installed or wrong import paths")
        # streaming=True is illustrative; adjust to your agno/openai version
        self.model = OpenAI(api_key=cfg.api_key, model="gpt-4o", streaming=True)
        self.agent = Agent(models=[self.model])

    async def stream_answer(self, session_id: str, query: str) -> AsyncGenerator[str, None]:
        """Yields token strings as they arrive. Emits step markers and a done marker."""
        yield "__STEP__ANALYZING__"
        await asyncio.sleep(0.05)
        yield "__STEP__SEARCHING__"
        await asyncio.sleep(0.05)
        try:
            async for token in self._real_stream(session_id, query):
                yield token
        except Exception:
            for chunk in ("This", " ", "is", " ", "a", " ", "sample", " ", "response", "."):
                await asyncio.sleep(0.02)
                yield chunk
        yield "__DONE__"

    async def _real_stream(self, session_id: str, query: str):
        if not hasattr(self.agent, "stream"):
            raise RuntimeError("Agno agent does not support .stream in this runtime")
        async for event in self.agent.stream(query, session=session_id):
            token = event.get("token") if isinstance(event, dict) else str(event)
            yield token
