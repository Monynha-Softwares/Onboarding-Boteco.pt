"""Helpers to interact with Supabase safely from Reflex states."""

from __future__ import annotations

import logging
import os
from typing import Any, Awaitable, Callable, List, Optional

import httpx
from postgrest import APIResponse
from supabase import Client, ClientOptions, create_client


class SupabaseClient:
    """A helper class to interact with the Supabase backend."""

    def __init__(self) -> None:
        self.url: Optional[str] = os.environ.get("SUPABASE_URL")
        self.key: Optional[str] = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get(
            "SUPABASE_KEY"
        )
        self.client: Optional[Client] = self._initialize_client()

    def _initialize_client(self) -> Optional[Client]:
        """Create a Supabase client if credentials are present."""

        if not self.url or not self.key:
            logging.warning("Supabase credentials not configured. Skipping client init.")
            return None
        try:
            return create_client(self.url, self.key, options=ClientOptions(schema="reflex"))
        except Exception as exc:  # pragma: no cover - defensive guard
            logging.exception("Error initializing Supabase client: %s", exc)
            return None

    def _require_client(self) -> Client:
        if not self.client:
            raise ConnectionError("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
        return self.client

    async def _execute(self, action: Callable[[Client], Awaitable[APIResponse]]) -> APIResponse:
        client = self._require_client()
        try:
            response = await action(client)
        except Exception as exc:
            logging.exception("Supabase request failed: %s", exc)
            raise
        error = getattr(response, "error", None)
        if error:
            message = getattr(error, "message", str(error))
            logging.error("Supabase returned an error: %s", message)
            raise ValueError(message)
        return response

    async def create_user(self, user_data: dict[str, Any]) -> List[dict[str, Any]]:
        """Insert a new user profile into the public `users` table."""

        response = await self._execute(
            lambda client: client.table("users").insert(user_data).execute()
        )
        return response.data or []

    async def upsert_user(self, user_data: dict[str, Any]) -> List[dict[str, Any]]:
        """Insert or update a user record based on email uniqueness."""

        response = await self._execute(
            lambda client: client.table("users").upsert(user_data, on_conflict="email").execute()
        )
        return response.data or []

    async def delete_boteco(self, boteco_id: str) -> APIResponse:
        """Delete a boteco record (used for rollbacks)."""

        return await self._execute(
            lambda client: client.table("boteco").delete().eq("id", boteco_id).execute()
        )

    async def create_boteco_and_associate_user(
        self, boteco_data: dict[str, Any], user_boteco_data: dict[str, Any]
    ) -> tuple[APIResponse, APIResponse]:
        """Create a boteco and associate the current user with basic rollback handling."""

        boteco_response = await self._execute(
            lambda client: client.table("boteco").insert(boteco_data).execute()
        )
        if not boteco_response.data:
            raise ValueError("Failed to create boteco. Nenhum dado retornado.")

        boteco_id = boteco_response.data[0]["id"]
        try:
            user_boteco_data["boteco_id"] = boteco_id
            user_boteco_response = await self._execute(
                lambda client: client.table("user_boteco").insert(user_boteco_data).execute()
            )
            if not user_boteco_response.data:
                raise ValueError("Falha ao associar o usuário ao boteco recém-criado.")
            return boteco_response, user_boteco_response
        except Exception as exc:
            logging.exception("Transaction failed, rolling back boteco creation: %s", exc)
            await self.delete_boteco(boteco_id)
            raise

    async def provision_schema(self, boteco_username: str) -> httpx.Response:
        """Call the internal API to provision a new schema for the boteco."""

        api_url = "http://localhost:8000/api/provision_org"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, json={"boteco_username": boteco_username})
                response.raise_for_status()
                return response
        except httpx.HTTPError as exc:
            logging.exception("Provisioning request failed: %s", exc)
            raise

    async def check_user_has_boteco(self, user_id: str) -> bool:
        """Check if a user is associated with any boteco."""

        response = await self._execute(
            lambda client: client.table("user_boteco").select("id", count="exact").eq("user_id", user_id).limit(1).execute()
        )
        return bool(getattr(response, "count", 0) > 0)

    async def get_user_by_email(self, email: str) -> List[dict[str, Any]]:
        """Return user records that match the given email (list)."""

        response = await self._execute(
            lambda client: client.table("users").select("*").eq("email", email).limit(1).execute()
        )
        return response.data or []


supabase_client = SupabaseClient()