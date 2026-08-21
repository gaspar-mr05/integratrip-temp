from app.db.supabase_client import get_supabase_client

class UserUpsertError(Exception):
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