import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import grpc
import llm_pb2

from app.clients.llm_client import (
    LlmClient,
    LlmEmptyResponseError,
    LlmInvalidRequestError,
    _raise_client_error,
)


def _rpc_error(code: grpc.StatusCode, details: str) -> grpc.aio.AioRpcError:
    return grpc.aio.AioRpcError(code, details=details)


def _client_with_stub(side_effect: list[object]) -> LlmClient:
    client = object.__new__(LlmClient)
    client._settings = SimpleNamespace(
        LLM_STUDENT_EMAIL="student@example.com",
        LLM_STUDENT_ID="12345678",
        LLM_GRPC_TIMEOUT_SECONDS=30,
        LLM_EMPTY_RESPONSE_MAX_ATTEMPTS=3,
        LLM_EMPTY_RESPONSE_RETRY_DELAY_SECONDS=0.25,
    )
    client._stub = SimpleNamespace(Generate=AsyncMock(side_effect=side_effect))
    return client


class LlmClientTests(unittest.TestCase):
    def test_classifies_empty_provider_response(self) -> None:
        rpc_error = grpc.aio.AioRpcError(
            grpc.StatusCode.INTERNAL,
            details="Gemini API error: Gemini returned an empty response.",
        )

        with self.assertRaises(LlmEmptyResponseError) as raised:
            _raise_client_error(rpc_error)

        self.assertEqual(
            str(raised.exception),
            "El proveedor del modelo devolvió una respuesta vacía",
        )


class LlmClientRetryTests(unittest.IsolatedAsyncioTestCase):
    async def test_retries_empty_responses_until_success(self) -> None:
        empty_response = _rpc_error(
            grpc.StatusCode.INTERNAL,
            "Gemini returned an empty response",
        )
        expected = llm_pb2.GenerateResponse(text="Respuesta", stop=True)
        client = _client_with_stub([empty_response, empty_response, expected])

        with patch(
            "app.clients.llm_client.asyncio.sleep",
            new=AsyncMock(),
        ) as sleep:
            response = await client.generate(llm_pb2.GenerateRequest())

        self.assertIs(response, expected)
        self.assertEqual(client._stub.Generate.await_count, 3)
        self.assertEqual(
            [call.args[0] for call in sleep.await_args_list],
            [0.25, 0.5],
        )

    async def test_stops_after_configured_empty_response_attempts(self) -> None:
        empty_responses = [
            _rpc_error(
                grpc.StatusCode.INTERNAL,
                "Gemini returned an empty response",
            )
            for _ in range(3)
        ]
        client = _client_with_stub(empty_responses)

        with patch(
            "app.clients.llm_client.asyncio.sleep",
            new=AsyncMock(),
        ), self.assertRaises(LlmEmptyResponseError):
            await client.generate(llm_pb2.GenerateRequest())

        self.assertEqual(client._stub.Generate.await_count, 3)

    async def test_does_not_retry_non_transient_client_errors(self) -> None:
        invalid_request = _rpc_error(
            grpc.StatusCode.INVALID_ARGUMENT,
            "Invalid request",
        )
        client = _client_with_stub([invalid_request])

        with patch(
            "app.clients.llm_client.asyncio.sleep",
            new=AsyncMock(),
        ) as sleep, self.assertRaises(LlmInvalidRequestError):
            await client.generate(llm_pb2.GenerateRequest())

        self.assertEqual(client._stub.Generate.await_count, 1)
        sleep.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
