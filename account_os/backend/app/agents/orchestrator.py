from typing import Annotated, TypedDict, List, Dict, Any, Union
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage
from .specialists import IntakeAgent, CodingAgent
from .workflow import ApprovalAgent, SyncAgent

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    next_agent: str
    client_id: str
    platform: str
    transaction_data: Dict[str, Any]
    status: str
    chart_of_accounts: List[Dict[str, Any]]
    rules: List[Dict[str, Any]]
    raw_text: str

class Orchestrator:
    """
    Supervisor Agent for AccountOS.
    Manages task routing between different specialized agents.
    """
    def __init__(self, connectors: Dict[str, Any] = None):
        self.intake_specialist = IntakeAgent()
        self.coding_specialist = CodingAgent()
        self.approval_specialist = ApprovalAgent()
        self.sync_specialist = SyncAgent(connectors)
        self.workflow = StateGraph(AgentState)
        self._build_graph()

    def _build_graph(self):
        self.workflow.add_node("intake", self.intake_node)
        self.workflow.add_node("coding", self.coding_node)
        self.workflow.add_node("approval", self.approval_node)
        self.workflow.add_node("sync", self.sync_node)
        self.workflow.add_node("supervisor", self.supervisor_node)

        self.workflow.set_entry_point("supervisor")

        self.workflow.add_conditional_edges(
            "supervisor",
            lambda x: x["next_agent"],
            {
                "intake": "intake",
                "coding": "coding",
                "approval": "approval",
                "sync": "sync",
                "end": END
            }
        )

        self.workflow.add_edge("intake", "supervisor")
        self.workflow.add_edge("coding", "supervisor")
        self.workflow.add_edge("approval", "supervisor")
        self.workflow.add_edge("sync", "supervisor")

        self.app = self.workflow.compile()

    async def supervisor_node(self, state: AgentState) -> Dict[str, Any]:
        if not state.get("transaction_data") and state.get("raw_text"):
            return {"next_agent": "intake"}

        status = state.get("status")
        if status == "ingested":
            return {"next_agent": "coding"}
        elif status == "coded":
            return {"next_agent": "approval"}
        elif status == "ready_to_sync":
            return {"next_agent": "sync"}
        elif status == "pending_approval":
            return {"next_agent": "end"}
        elif status == "synced":
            return {"next_agent": "end"}

        return {"next_agent": "end"}

    async def intake_node(self, state: AgentState) -> Dict[str, Any]:
        print("--- INTAKE AGENT ---")
        result = await self.intake_specialist.process_document(state["raw_text"])
        return {"status": "ingested", "transaction_data": result}

    async def coding_node(self, state: AgentState) -> Dict[str, Any]:
        print("--- CODING AGENT ---")
        coa = state.get("chart_of_accounts", [])
        result = await self.coding_specialist.suggest_gl_code(state["transaction_data"], coa)
        return {
            "status": "coded",
            "transaction_data": {**state["transaction_data"], "gl_code": result.get("gl_code")}
        }

    async def approval_node(self, state: AgentState) -> Dict[str, Any]:
        print("--- APPROVAL AGENT ---")
        rules = state.get("rules", [])
        result = await self.approval_specialist.process_approval(state["transaction_data"], rules)
        return {
            "status": result["status"],
            "transaction_data": {**state["transaction_data"], "approval_reason": result.get("approval_reason")}
        }

    async def sync_node(self, state: AgentState) -> Dict[str, Any]:
        print("--- SYNC AGENT ---")
        platform = state.get("platform", "qbo")
        result = await self.sync_specialist.sync_transaction(platform, state["transaction_data"])
        return {"status": "synced", "sync_result": result}

    async def run(self, initial_state: AgentState):
        async for output in self.app.astream(initial_state):
            for key, value in output.items():
                print(f"Output from node '{key}': {value}")
        return output
