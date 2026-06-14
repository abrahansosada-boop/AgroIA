from collections.abc import MutableMapping
from typing import Any, Protocol

import streamlit as st
from supabase import Client, create_client

from agroia.config import AppConfig, DataBackend
from agroia.demo_supabase import DemoSupabaseClient

DEMO_CLIENT_SESSION_KEY = "_agroia_demo_database_client"


class DatabaseClient(Protocol):
    def table(self, name: str) -> Any: ...


@st.cache_resource
def init_supabase_connection(url: str, key: str) -> Client:
    return create_client(url, key)


def create_database_client(
    app_config: AppConfig,
    session_state: MutableMapping[str, Any],
) -> DatabaseClient:
    if app_config.data_backend is DataBackend.DEMO:
        client = session_state.get(DEMO_CLIENT_SESSION_KEY)
        if not isinstance(client, DemoSupabaseClient):
            client = DemoSupabaseClient()
            session_state[DEMO_CLIENT_SESSION_KEY] = client
        return client

    if app_config.supabase_url is None or app_config.supabase_key is None:
        raise ValueError("Supabase credentials are required for the Supabase backend")

    return init_supabase_connection(
        app_config.supabase_url,
        app_config.supabase_key,
    )
