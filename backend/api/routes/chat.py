from fastapi import APIRouter, HTTPException
from backend.api.models.schemas import ChatRequest, ChatResponse
from backend.agent.graph import qa_graph
from backend.agent.state import AgentState

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        state: AgentState = {
            "neighborhood": req.neighborhood,
            "city": req.city,
            "query": req.query,
            "chat_history": req.chat_history,
            "raw_data": req.raw_data or {},
            "market_signals": req.market_signals or {},
            "confidence_score": req.confidence_score or {},
            "report": req.report or "",
            "processing_steps": [],
            "sources": [],
        }
        result = qa_graph.invoke(state)
        return ChatResponse(
            response=result.get("chat_response", ""),
            chat_history=result.get("chat_history", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))