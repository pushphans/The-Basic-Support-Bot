from fastapi import APIRouter, HTTPException
from langchain.messages import HumanMessage
from app.agent.graph import AgentState
from app.models.request_model import RequestModel
from app.agent.graph import workflow
from app.models.response_model import ResponseModel

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Welcome to the Basic Support Bot API!"}


@router.post("/route")
async def get_support(request: RequestModel):

    try:

        initial_state: AgentState = {
            "messages": [HumanMessage(content=request.user_message)],
            "intent": None,
        }

        final_state: AgentState = await workflow.ainvoke(initial_state)
        final_response = final_state["messages"][-1].content

        return ResponseModel(ai_response=final_response, intent=final_state["intent"])

    except Exception as e:

        raise HTTPException(detail=str(e), status_code=500)
