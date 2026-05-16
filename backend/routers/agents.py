"""Debug routes — run individual agents in isolation."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from schemas.requests import AgentDebugRequest
from agents.news_parser import NewsParserAgent
from agents.impact_analyzer import ImpactAnalyzerAgent
from agents.action_generator import ActionGeneratorAgent
from agents.output_composer import OutputComposerAgent

router = APIRouter(prefix="/api/v1/agents", tags=["debug"])

_AGENT_MAP = {
    "news_parser": NewsParserAgent,
    "impact_analyzer": ImpactAnalyzerAgent,
    "action_generator": ActionGeneratorAgent,
    "output_composer": OutputComposerAgent,
}


@router.post("/{agent_name}")
async def run_single_agent(agent_name: str, req: AgentDebugRequest):
    """Run one agent in isolation for debugging.

    Returns that agent's validated output.
    """
    agent_cls = _AGENT_MAP.get(agent_name)
    if agent_cls is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agent: {agent_name}. Valid: {list(_AGENT_MAP.keys())}",
        )

    agent = agent_cls()
    result = await agent.run(req.input_data)
    return {"agent": agent_name, "output": result}
