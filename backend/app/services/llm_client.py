from typing import NoReturn

import grpc

import llm_pb2
import llm_pb2_grpc
from app.config import Settings, get_settings


class LlmClientError(Exception):
    pass


class LlmRateLimitError(LlmClientError):
    pass


class LlmAuthenticationError(LlmClientError):
    pass


class LlmInvalidRequestError(LlmClientError):
    pass


def _create_channel(settings: Settings) -> grpc.aio.Channel:
    if settings.LLM_GRPC_TLS:
        credentials = grpc.ssl_channel_credentials()
        return grpc.aio.secure_channel(settings.LLM_GRPC_TARGET, credentials)

    return grpc.aio.insecure_channel(settings.LLM_GRPC_TARGET)


def _raise_client_error(exc: grpc.aio.AioRpcError) -> NoReturn:
    code = exc.code()

    if code == grpc.StatusCode.RESOURCE_EXHAUSTED:
        raise LlmRateLimitError(
            "Se alcanzó el límite de solicitudes al servicio LLM"
        ) from exc
    if code in (grpc.StatusCode.UNAUTHENTICATED, grpc.StatusCode.PERMISSION_DENIED):
        raise LlmAuthenticationError(
            "El servicio LLM rechazó las credenciales configuradas"
        ) from exc
    if code == grpc.StatusCode.INVALID_ARGUMENT:
        raise LlmInvalidRequestError(
            "El servicio LLM rechazó la solicitud enviada"
        ) from exc

    raise LlmClientError("No se pudo obtener una respuesta del servicio LLM") from exc


class LlmClient:
    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._channel = _create_channel(self._settings)
        self._stub = llm_pb2_grpc.LlmStub(self._channel)

    async def __aenter__(self) -> "LlmClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()

    async def close(self) -> None:
        await self._channel.close()

    async def generate(
        self,
        request: llm_pb2.GenerateRequest,
    ) -> llm_pb2.GenerateResponse:
        metadata = (
            ("x-student-email", self._settings.LLM_STUDENT_EMAIL),
            ("x-student-id", self._settings.LLM_STUDENT_ID),
        )

        try:
            return await self._stub.Generate(
                request,
                metadata=metadata,
                timeout=self._settings.LLM_GRPC_TIMEOUT_SECONDS,
            )
        except grpc.aio.AioRpcError as exc:
            _raise_client_error(exc)
