import asyncio

from langchain_core.messages import HumanMessage

from agent_builder import build_memory_rag_agent


async def main():
    app, tools = await build_memory_rag_agent()

    print("\nLoaded tools:")
    for tool in tools:
        print(f"- {tool.name}")

    while True:
        question = input("\nAsk a policy question, or type 'exit': ")

        if question.lower().strip() in {"exit", "quit"}:
            break

        result = await app.ainvoke(
            {
                "messages": [
                    HumanMessage(content=question)
                ]
            }
        )

        print("\nAnswer:")
        print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())