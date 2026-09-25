import llm_pb2

ROLE_NAMES = {
    llm_pb2.Message.USER: "user",
    llm_pb2.Message.MODEL: "model",
    llm_pb2.Message.TOOL: "tool",
}
ROLE_VALUES = {name: value for value, name in ROLE_NAMES.items()}


class RoleUnspecifiedError(Exception):
    pass


class NegativeSequenceNumberError(Exception):
    pass


class InvalidStoredMessageError(Exception):
    pass


def transform_message_to_dict(message: llm_pb2.Message, sequence_number: int) -> dict:
    if sequence_number < 0:
        raise NegativeSequenceNumberError(
            "El número de secuencia debe ser mayor o igual a 0"
        )

    try:
        role = ROLE_NAMES[message.role]
    except KeyError as exc:
        raise RoleUnspecifiedError(
            "El mensaje no tiene un rol válido"
        ) from exc

    return {
        "role": role,
        "text": message.text,
        "function_calls": [
            {
                "id": fc.id,
                "name": fc.name,
                "arguments_json": fc.arguments_json,
            }
            for fc in message.function_calls
        ],
        "function_results": [
            {
                "id": result.id,
                "name": result.name,
                "result_json": result.result_json,
                "is_error": result.is_error,
            }
            for result in message.function_results
        ],
        "sequence": sequence_number,
    }


def transform_dict_to_message(message_dict: dict) -> llm_pb2.Message:
    try:
        role = ROLE_VALUES[message_dict["role"]]
    except (KeyError, TypeError) as exc:
        raise RoleUnspecifiedError(
            "El mensaje no tiene un rol válido"
        ) from exc

    try:
        text = message_dict["text"]
        function_calls_data = message_dict["function_calls"]
        function_results_data = message_dict["function_results"]
    except (KeyError, TypeError) as exc:
        raise InvalidStoredMessageError(
            "El mensaje persistido tiene una estructura inválida"
        ) from exc

    if (
        not isinstance(text, str)
        or not isinstance(function_calls_data, list)
        or not isinstance(function_results_data, list)
    ):
        raise InvalidStoredMessageError(
            "El mensaje persistido tiene una estructura inválida"
        )

    function_calls = []
    for function_call_data in function_calls_data:
        if not isinstance(function_call_data, dict):
            raise InvalidStoredMessageError(
                "La llamada a tool persistida tiene una estructura inválida"
            )
        try:
            function_call = llm_pb2.FunctionCall(
                id=function_call_data["id"],
                name=function_call_data["name"],
                arguments_json=function_call_data["arguments_json"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidStoredMessageError(
                "La llamada a tool persistida tiene una estructura inválida"
            ) from exc
        function_calls.append(function_call)

    function_results = []
    for function_result_data in function_results_data:
        if not isinstance(function_result_data, dict):
            raise InvalidStoredMessageError(
                "El resultado de tool persistido tiene una estructura inválida"
            )
        try:
            function_result = llm_pb2.FunctionResult(
                id=function_result_data["id"],
                name=function_result_data["name"],
                result_json=function_result_data["result_json"],
                is_error=function_result_data["is_error"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidStoredMessageError(
                "El resultado de tool persistido tiene una estructura inválida"
            ) from exc
        function_results.append(function_result)

    return llm_pb2.Message(
        role=role,
        text=text,
        function_calls=function_calls,
        function_results=function_results,
    )
