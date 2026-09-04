from functools import lru_cache

import httpx
from supabase import Client, create_client
from supabase.lib.client_options import SyncClientOptions

from app.config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    settings = get_settings()
    http_client = httpx.Client(
        http2=settings.SUPABASE_HTTP2_ENABLED,
        timeout=settings.SUPABASE_HTTP_TIMEOUT_SECONDS,
        follow_redirects=True,
    )
    options = SyncClientOptions(httpx_client=http_client)
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
        options=options,
    )
