import asyncio
import json
from typing import Annotated, TypedDict, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def extract_text_messages(messages) -> str:
    """
    Convert message trace into plain text for reflection.
    """
    parts = []

    for message in messages:
        msg_type = type(message).__name__

        if isinstance(message, SystemMessage):
            continue

        if getattr(message, "tool_calls", None):
            parts.append(f"{msg_type}: tool_calls={message.tool_calls}")
        else:
            parts.append(f"{msg_type}: {message.content}")

    return "\n\n".join(parts)


def parse_reflection_json(text: str) -> dict:
    """
    Best-effort parser for reflection JSON.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "save_lesson": False,
            "lesson": "",
            "reason": "Reflection output was not valid JSON.",
        }


async def main():
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

    print("\nLoaded MCP tools:")
    for tool in tools:
        print(f"- {tool.name}")

    save_memory_tool = next(tool for tool in tools if tool.name == "save_memory")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    reflection_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    system_message = SystemMessage(
        content=(
            "You are a memory-aware company policy assistant.\n\n"
            "Available capabilities:\n"
            "1. Use search_memory to check prior user preferences, corrections, or lessons.\n"
            "2. Use search_policy_docs to answer company policy questions using retrieved context.\n"
            "3. Use save_memory only when the user gives a durable preference, correction, or reusable lesson.\n\n"
            "Rules:\n"
            "- Before answering any user question, always call search_memory once using the user's question as the query.\n"
            "- For company policy questions, use search_policy_docs after checking memory.\n"
            "- Base policy answers only on retrieved policy context.\n"
            "- Mention the source document when possible.\n"
            "- If retrieved context is insufficient, say you do not have enough information.\n"
            "- Do not save trivial memories during normal answering unless the user gives a durable preference or correction.\n"
        )
    )

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

    test_questions = [
        "How many annual leave days do employees in India get?",
        "What should I do if I receive a phishing email?",
        "When do I need to submit travel expenses?",
    ]

    for question in test_questions:
        print("\n" + "=" * 100)
        print(f"USER QUESTION: {question}")

        result = await app.ainvoke(
            {
                "messages": [
                    HumanMessage(content=question)
                ]
            }
        )

        final_answer = result["messages"][-1].content
        trace_text = extract_text_messages(result["messages"])

        print("\nConversation trace:")
        print(trace_text)

        print("\nFinal answer:")
        print(final_answer)

        reflection_prompt = f"""
You are evaluating a RAG agent's answer.

Your job:
1. Check whether the answer was grounded in retrieved policy context.
2. Check whether it mentioned the source document when possible.
3. Check whether there is a reusable lesson that could improve future answers.

Only save a lesson if it is broadly reusable.
Do not save one-off facts from the policy document.
Do not save trivial observations.

Return only valid JSON in this exact format:

{{
  "save_lesson": true or false,
  "lesson": "short reusable lesson, or empty string",
  "reason": "brief reason"
}}

User question:
{question}

Agent trace:
{trace_text}

Final answer:
{final_answer}
"""

        reflection = await reflection_llm.ainvoke(reflection_prompt)
        reflection_data = parse_reflection_json(reflection.content)

        print("\nReflection:")
        print(reflection_data)

        if reflection_data.get("save_lesson") and reflection_data.get("lesson"):
            save_result = await save_memory_tool.ainvoke(
                {
                    "memory_type": "lesson",
                    "content": reflection_data["lesson"],
                    "source": "agent_reflection",
                }
            )

            print("\nSaved reflection lesson:")
            print(save_result)
        else:
            print("\nNo reusable lesson saved.")


if __name__ == "__main__":
    asyncio.run(main())