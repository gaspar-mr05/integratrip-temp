from postgrest.exceptions import APIError

from app.clients.supabase_client import get_supabase_client


class UserUpsertError(Exception):
    pass


class UserReadError(Exception):
    pass


def upsert_user(as_subject: str, email: str | None) -> dict:
    supabase = get_supabase_client()
    result = (
        supabase.table("users")
        .upsert({"as_subject": as_subject, "email": email}, on_conflict="as_subject")
        .execute()
    )
    if not result.data:
        raise UserUpsertError("No se pudo crear/actualizar el usuario")
    return result.data[0]


def get_user(*, user_id: str) -> dict | None:
    try:
        result = (
            get_supabase_client()
            .table("users")
            .select("id,email")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
    except APIError as exc:
        raise UserReadError("No se pudo obtener el usuario") from exc

    return result.data[0] if result.data else None
