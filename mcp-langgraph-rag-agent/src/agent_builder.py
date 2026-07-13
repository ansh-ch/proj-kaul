from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


DEFAULT_SYSTEM_PROMPT = (
    "You are a memory-aware company policy assistant.\n\n"
    "Available capabilities:\n"
    "1. Use search_memory to check prior user preferences, corrections, or lessons.\n"
    "2. Use search_policy_docs to answer company policy questions using retrieved context.\n"
    "3. Use save_memory only when the user gives a durable preference, correction, or reusable lesson.\n\n"
    "Rules:\n"
    "- Before answering any user question, always call search_memory once using the user's question as the query.\n"
    "- For company policy questions, use search_policy_docs after checking memory.\n"
    "- Base policy answers only on retrieved policy context.\n"
    "- Mention the source document name when possible.\n"
    "- If retrieved context is insufficient, say you do not have enough information.\n"
    "- Keep answers concise.\n"
    "- Do not save trivial memories during normal answering unless the user gives a durable preference or correction.\n"
)


async def load_mcp_tools():
    client = MultiServerMCPClient(
        {
            "policy_rag": {
                "command": "python",
                "args": ["src/rag_mcp_server.py"],
                "transport": "stdio",
            },
            "memory": {
                "command": "python",
                "args": ["src/memory_mcp_server.py"],
                "transport": "stdio",
            },
        }
    )

    tools = await client.get_tools()
    return tools


async def build_memory_rag_agent(
    model: str = "gpt-4o-mini",
    temperature: float = 0,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
):
    tools = await load_mcp_tools()

    llm = ChatOpenAI(model=model, temperature=temperature)
    llm_with_tools = llm.bind_tools(tools)

    system_message = SystemMessage(content=system_prompt)

    async def call_model(state: AgentState):
        messages = state["messages"]

        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [system_message] + messages

        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last_message = state["messages"][-1]

        if getattr(last_message, "tool_calls", None):
            return "tools"

        return END

    graph = StateGraph(AgentState)

    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph.add_edge("tools", "agent")

    app = graph.compile()

    return app, tools