import asyncio

import llm_pb2

from app.clients.llm_client import LlmClient, LlmClientError


async def main() -> None:
    message = llm_pb2.Message(
        role=llm_pb2.Message.USER,
        text="Escribe un mensaje breve",
    )
    request = llm_pb2.GenerateRequest(
        messages=[message],
        tools=[],
    )

    try:
        async with LlmClient() as client:
            response = await client.generate(request)

    except LlmClientError as exc:
        print(f"Error consultando el LLM: {exc}")
        return
    print(response.text)
    print(response.stop)
    print(response.model)
    for function_call in response.function_calls:
        print("function_call:")


if __name__ == "__main__":
    asyncio.run(main())
