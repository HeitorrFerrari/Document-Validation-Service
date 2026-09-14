from langgraph.graph import END, START, StateGraph

from app.agents.feedback.agent import build_feedback
from app.agents.validator.agent import validate_eligibility
from app.api.extraction.extract_data import extrair_curriculo
from app.core.tracing import trace
from app.states.state import GraphState


def extract_node(state: GraphState) -> dict:
    trace("graph", "extract_node", resume_text_chars=len(state["resume_text"]))
    resume = extrair_curriculo(state["resume_text"])
    trace(
        "graph", "extract_node_done",
        candidate_name=resume.name,
        skills=len(resume.skills),
        experiences=len(resume.experience),
    )
    return {"resume": resume}

def validation_node(state: GraphState) -> dict:
    trace("graph", "validation_node", candidate_name=state["resume"].name)
    resultado = validate_eligibility(state["resume"], state["job_requirements"])
    trace(
        "graph", "validation_node_done",
        score=resultado.score,
        is_eligible=resultado.is_eligible,
    )
    return {"validation": resultado}

def feedback_node(state: GraphState) -> dict:
    trace("graph", "feedback_node", score=state["validation"].score)
    texto = build_feedback(state["validation"])
    trace("graph", "feedback_node_done", feedback_chars=len(texto))
    return {"feedback": texto}

graph = StateGraph(GraphState)
graph.add_node("extract", extract_node)
graph.add_node("validation", validation_node)
graph.add_node("feedback", feedback_node)

graph.add_edge(START, "extract")
graph.add_edge("extract", "validation")
graph.add_edge("validation", "feedback")
graph.add_edge("feedback", END)

app_graph = graph.compile()