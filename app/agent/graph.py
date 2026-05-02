from typing import Literal, Optional, TypedDict, Annotated
from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, SystemMessage
from langgraph.graph import START, StateGraph, add_messages
from pydantic import BaseModel, Field
from app.core.config import settings

# -----------------------
# LLM INITIALIZATION
# -----------------------
llm = init_chat_model(
    "gpt-4o-mini", model_provider="openai", api_key=settings.OPENAI_API_KEY
)


# -----------------------
# STRUCTURED OUTPUT
# -----------------------
class IntentOutput(BaseModel):
    Intent: Literal["tech", "refund", "general"] = Field(
        description="The intent of the user's message, either 'tech' for technical issues, 'refund' for refund requests, or 'general' for general inquiries."
    )


intent_llm = llm.with_structured_output(schema=IntentOutput)


# -----------------------
# AGENT STATE
# -----------------------
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    intent: Optional[str]


# -----------------------
# NODES DEFINITION
# -----------------------
async def manager_node(state: AgentState) -> AgentState:
    user_message = state["messages"][-1]

    system_message = SystemMessage(content=f"""
You are an intent classifier for a customer support chatbot. Your task is to analyze the user's message and determine whether the intent is related to "tech" issues, "refund" requests, or "general" inquiries.
""")

    response: IntentOutput = await intent_llm.ainvoke([system_message, user_message])

    return {"intent": response.Intent}




async def routing_after_manager_function(state: AgentState) -> Literal["tech", "refund", "general"]:
    pass


async def tech_node(state: AgentState) -> AgentState:
    user_message = state["messages"][-1]

    system_message = SystemMessage(
        content=f"""You are a technical support agent for a customer support chatbot. Your task is to assist the user with their technical issues based on their message. Please provide a helpful response to address their concerns.
"""
    )

    response = await llm.ainvoke([system_message, user_message])

    return {"messages": [response]}


async def refund_node(state: AgentState) -> AgentState:
    user_message = state["messages"][-1]

    system_message = SystemMessage(
        content=f"""You are a refund request handler for a customer support chatbot. Your task is to assist the user with their refund requests based on their message. Please provide a helpful response to address their concerns.
"""
    )

    response = await llm.ainvoke([system_message, user_message])

    return {"messages": [response]}


async def general_node(state: AgentState) -> AgentState:
    user_message = state["messages"][-1]

    system_message = SystemMessage(
        content=f"""You are a general support agent for a customer support chatbot. Your task is to assist the user with their general inquiries based on their message. Please provide a helpful response to address their concerns.
"""
    )

    response = await llm.ainvoke([system_message, user_message])

    return {"messages": [response]}


# -----------------------
# GRAPH DEFINITION
# -----------------------
graph = StateGraph(state_schema=AgentState)

graph.add_node("manager_node", manager_node)
graph.add_node("tech_node", tech_node)
graph.add_node("refund_node", refund_node)
graph.add_node("general_node", general_node)

graph.add_edge(START, "manager_node")
graph.add_conditional_edges("manager_node", )