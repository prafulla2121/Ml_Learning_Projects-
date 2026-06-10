from typing import Annotated, TypedDict, List, Dict, Any, Union
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    next_agent: str
    client_id: str
    transaction_data: Dict[str, Any]
    status: str

class Orchestrator:
    """
    Supervisor Agent for AccountOS.
    Manages task routing between different specialized agents.
    """
    def __init__(self):
        self.workflow = StateGraph(AgentState)
        self._build_graph()

    def _build_graph(self):
        # Define nodes
        self.workflow.add_node("intake", self.intake_agent)
        self.workflow.add_node("coding", self.coding_agent)
        self.workflow.add_node("compliance", self.compliance_agent)
        self.workflow.add_node("sync", self.sync_agent)
        self.workflow.add_node("supervisor", self.supervisor_node)

        # Define edges
        self.workflow.set_entry_point("supervisor")

        self.workflow.add_conditional_edges(
            "supervisor",
            lambda x: x["next_agent"],
            {
                "intake": "intake",
                "coding": "coding",
                "compliance": "compliance",
                "sync": "sync",
                "end": END
            }
        )

        self.workflow.add_edge("intake", "supervisor")
        self.workflow.add_edge("coding", "supervisor")
        self.workflow.add_edge("compliance", "supervisor")
        self.workflow.add_edge("sync", "supervisor")

        self.app = self.workflow.compile()

    async def supervisor_node(self, state: AgentState) -> Dict[str, Any]:
        """Routes the task to the appropriate agent based on current state."""
        # Simplified logic for Phase 0
        if not state.get("transaction_data"):
            return {"next_agent": "intake"}

        status = state.get("status")
        if status == "ingested":
            return {"next_agent": "coding"}
        elif status == "coded":
            return {"next_agent": "compliance"}
        elif status == "validated":
            return {"next_agent": "sync"}
        elif status == "synced":
            return {"next_agent": "end"}

        return {"next_agent": "end"}

    async def intake_agent(self, state: AgentState) -> Dict[str, Any]:
        print("--- INTAKE AGENT ---")
        # Logic to process document
        return {"status": "ingested", "transaction_data": {"vendor": "Generic", "amount": 100.0}}

    async def coding_agent(self, state: AgentState) -> Dict[str, Any]:
        print("--- CODING AGENT ---")
        # Logic to map GL codes
        return {"status": "coded", "transaction_data": {**state["transaction_data"], "gl_code": "6000"}}

    async def compliance_agent(self, state: AgentState) -> Dict[str, Any]:
        print("--- COMPLIANCE AGENT ---")
        # Logic to validate transaction
        return {"status": "validated"}

    async def sync_agent(self, state: AgentState) -> Dict[str, Any]:
        print("--- SYNC AGENT ---")
        # Logic to sync with accounting platform
        return {"status": "synced"}

    async def run(self, initial_state: AgentState):
        async for output in self.app.astream(initial_state):
            for key, value in output.items():
                print(f"Output from node '{key}': {value}")
        return output
