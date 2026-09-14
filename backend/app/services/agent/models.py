from dataclasses import dataclass

import llm_pb2


@dataclass(frozen=True)
class PendingToolConfirmation:
    function_call_id: str
    llm_name: str
    arguments_json: str


@dataclass(frozen=True)
class AgentRunResult:
    final_response: llm_pb2.GenerateResponse | None
    generated_messages: tuple[llm_pb2.Message, ...]
    pending_confirmations: tuple[PendingToolConfirmation, ...] = ()

