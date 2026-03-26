from langgraph.graph import StateGraph, END
from backend.agent.state import AgentState
from backend.agent.nodes.data_fetcher import data_fetcher_node
from backend.agent.nodes.analyzer import analyzer_node
from backend.agent.nodes.scorer import scorer_node
from backend.agent.nodes.reporter import reporter_node
from backend.agent.nodes.qa_agent import qa_agent_node


def _route_after_entry(state: AgentState) -> str:
    """Route to Q&A if query present, else full analysis pipeline."""
    if state.get("query") and state.get("raw_data"):
        return "qa_agent"
    return "data_fetcher"


def build_analysis_graph() -> StateGraph:
    """Full analysis pipeline: fetch → analyze → score → report."""
    graph = StateGraph(AgentState)

    graph.add_node("data_fetcher", data_fetcher_node)
    graph.add_node("analyzer",     analyzer_node)
    graph.add_node("scorer",       scorer_node)
    graph.add_node("reporter",     reporter_node)

    graph.set_entry_point("data_fetcher")
    graph.add_edge("data_fetcher", "analyzer")
    graph.add_edge("analyzer",     "scorer")
    graph.add_edge("scorer",       "reporter")
    graph.add_edge("reporter",     END)

    return graph.compile()


def build_qa_graph() -> StateGraph:
    """Q&A only: uses pre-loaded state, goes straight to qa_agent."""
    graph = StateGraph(AgentState)
    graph.add_node("qa_agent", qa_agent_node)
    graph.set_entry_point("qa_agent")
    graph.add_edge("qa_agent", END)
    return graph.compile()


# Compiled singletons
analysis_graph = build_analysis_graph()
qa_graph       = build_qa_graph()