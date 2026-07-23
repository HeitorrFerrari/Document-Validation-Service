from langgraph.graph import END, START, StateGraph

from app.agents.feedback.agent import build_feedback
from app.agents.validator.agent import validate_eligibility
from app.api.extraction.extract_data import extrair_curriculo
from app.states.state import GraphState


def extract_node(state: GraphState) -> dict:
    resume = extrair_curriculo(state["resume_text"])
    return {"resume": resume}

def validation_node(state: GraphState) -> dict:
    resultado = validate_eligibility(state["resume"], state["job_requirements"])
    return {"validation": resultado}

def feedback_node(state: GraphState) -> dict:
    texto = build_feedback(state["validation_text"])
    return {"feedback": texto}

