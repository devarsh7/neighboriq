from fastapi import APIRouter, HTTPException
from backend.api.models.schemas import AnalyzeRequest, AnalyzeResponse, CompareRequest
from backend.agent.graph import analysis_graph
from backend.agent.state import AgentState

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_neighborhood(req: AnalyzeRequest):
    try:
        initial_state: AgentState = {
            "neighborhood": req.neighborhood,
            "city": req.city,
            "processing_steps": [],
            "sources": [],
            "chat_history": [],
        }
        result = analysis_graph.invoke(initial_state)

        return AnalyzeResponse(
            neighborhood=result["raw_data"]["neighborhood"],
            city=result["raw_data"]["city"],
            raw_data=result["raw_data"],
            market_signals=result["market_signals"],
            confidence_score=result["confidence_score"],
            report=result["report"],
            report_bullets=result.get("report_bullets", []),
            sources=result.get("sources", []),
            processing_steps=result.get("processing_steps", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_neighborhoods(req: CompareRequest):
    results = []
    for n in req.neighborhoods[:3]:  # max 3
        try:
            state: AgentState = {
                "neighborhood": n.neighborhood,
                "city": n.city,
                "processing_steps": [],
                "sources": [],
                "chat_history": [],
            }
            r = analysis_graph.invoke(state)
            results.append({
                "neighborhood": r["raw_data"]["neighborhood"],
                "city": r["raw_data"]["city"],
                "raw_data": r["raw_data"],
                "confidence_score": r["confidence_score"],
                "report_bullets": r.get("report_bullets", []),
            })
        except Exception as e:
            results.append({"error": str(e), "neighborhood": n.neighborhood})
    return {"comparisons": results}