import asyncio
import json
from typing import Annotated, TypedDict

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


TEST_CASES = [
    {
        "name": "india_annual_leave",
        "question": "How many annual leave days do employees in India get?",
        "expected_contains": ["18", "HR Leave Policy"],
    },
    {
        "name": "phishing_email",
        "question": "What should I do if I receive a phishing email?",
        "expected_contains": ["reported", "IT security", "IT Security Policy"],
    },
    {
        "name": "travel_expenses",
        "question": "When do I need to submit travel expenses?",
        "expected_contains": ["30 days", "Travel Reimbursement Policy"],
    },
]


def simple_check(answer: str, expected_contains: list[str]) -> tuple[bool, list[str]]:
    missing = []

    answer_lower = answer.lower()

    for expected in expected_contains:
        if expected.lower() not in answer_lower:
            missing.append(expected)

    return len(missing) == 0, missing


async def build_agent():
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

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    system_message = SystemMessage(
        content=(
            "You are a memory-aware company policy assistant.\n\n"
            "Rules:\n"
            "- Before answering any user question, always call search_memory once using the user's question as the query.\n"
            "- For company policy questions, use search_policy_docs after checking memory.\n"
            "- Base policy answers only on retrieved policy context.\n"
            "- Mention the source document name when possible.\n"
            "- If retrieved context is insufficient, say you do not have enough information.\n"
            "- Keep answers concise.\n"
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

    return graph.compile()


async def main():
    app = await build_agent()

    eval_results = []

    for test_case in TEST_CASES:
        print("\n" + "=" * 100)
        print(f"Running test: {test_case['name']}")
        print(f"Question: {test_case['question']}")

        result = await app.ainvoke(
            {
                "messages": [
                    HumanMessage(content=test_case["question"])
                ]
            }
        )

        answer = result["messages"][-1].content
        passed, missing = simple_check(answer, test_case["expected_contains"])

        eval_result = {
            "test_name": test_case["name"],
            "question": test_case["question"],
            "answer": answer,
            "expected_contains": test_case["expected_contains"],
            "passed": passed,
            "missing": missing,
        }

        eval_results.append(eval_result)

        print("\nAnswer:")
        print(answer)

        print("\nResult:")
        print("PASS" if passed else "FAIL")

        if missing:
            print("Missing expected terms:", missing)

    passed_count = sum(1 for item in eval_results if item["passed"])
    total_count = len(eval_results)

    print("\n" + "=" * 100)
    print("EVALUATION SUMMARY")
    print(f"Passed: {passed_count}/{total_count}")
    print(f"Accuracy: {passed_count / total_count:.0%}")

    with open("data/eval_results.json", "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    print("\nSaved detailed results to data/eval_results.json")


if __name__ == "__main__":
    asyncio.run(main())