"""Authentication helpers for the Boteco onboarding flow."""

from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

import reflex as rx

from app.services.supabase_client import supabase_client
from app.states.onboarding_state import OnboardingState


class AuthState(rx.State):
    """Custom auth state to register/sign-in users into the onboarding flow."""

    @staticmethod
    def _prefill_onboarding(user: Dict[str, Any]) -> None:
        """Populate onboarding fields from a user payload."""

        OnboardingState.user_id = user.get("id")
        OnboardingState.personal_first_name = user.get("first_name", "")
        OnboardingState.personal_last_name = user.get("last_name", "")
        OnboardingState.personal_email = user.get("email", "")
        OnboardingState.personal_tax_number = user.get("tax_number", "")
        OnboardingState.personal_birth_date = user.get("birth_date", "")
        OnboardingState.personal_country = user.get("country", "Brasil")
        OnboardingState.personal_postal_code = user.get("postal_code", "")
        OnboardingState.personal_house_number = user.get("house_number", "")
        OnboardingState.current_step = 1

    @staticmethod
    def _build_user_payload(form_data: Dict[str, Any]) -> Tuple[Dict[str, Any], str | None]:
        """Extract and validate registration fields from the form."""

        first_name = form_data.get("personal_first_name", "").strip()
        last_name = form_data.get("personal_last_name", "").strip()
        email = form_data.get("personal_email", "").strip()
        password = form_data.get("password", "").strip()
        tax_number = form_data.get("personal_tax_number", "").strip()
        birth_date = form_data.get("personal_birth_date", "").strip()
        country = form_data.get("personal_country", "Brasil").strip() or "Brasil"
        postal_code = form_data.get("personal_postal_code", "").strip()
        house_number = form_data.get("personal_house_number", "").strip()

        if not all([first_name, last_name, email, password]):
            return {}, "Preencha nome, sobrenome, email e senha para continuar."
        if len(password) < 6:
            return {}, "A senha deve ter pelo menos 6 caracteres."

        username_hint = (
            f"{first_name.lower()}.{last_name.lower()}{tax_number[:4]}"
            if tax_number
            else f"{first_name.lower()}.{last_name.lower()}"
        )

        user_data = {
            "email": email,
            "username": username_hint,
            "tax_number": tax_number or "N/A",
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date or "1900-01-01",
            "country": country or "Brasil",
            "postal_code": postal_code,
            "house_number": house_number,
            "is_owner": True,
        }
        return user_data, None

    @classmethod
    async def _perform_register(
        cls, form_data: Dict[str, Any], client=supabase_client
    ) -> Tuple[str | None, str | None]:
        """Shared registration logic to ease testing."""

        user_data, error = cls._build_user_payload(form_data)
        if error:
            return None, error
        try:
            created = await client.create_user(user_data)
            if not created:
                return None, "Não foi possível criar a conta. Tente novamente."
            cls._prefill_onboarding(created[0])
            return "/onboarding/step-1-personal", None
        except Exception as exc:  # pragma: no cover - guarded by tests on helpers
            logging.exception("Failed to register user: %s", exc)
            return None, f"Falha ao criar conta: {exc}"

    @rx.event
    async def register(self, form_data: dict):
        redirect_to, error = await self._perform_register(form_data)
        if error:
            yield rx.toast.error(error)
            return
        yield rx.redirect(redirect_to)

    @classmethod
    async def _perform_signin(
        cls, form_data: Dict[str, Any], client=supabase_client
    ) -> Tuple[str | None, str | None]:
        """Shared sign-in logic used by the event handler and tests."""

        email = form_data.get("email", "").strip()
        if not email:
            return None, "Forneça um email para entrar."
        try:
            users = await client.get_user_by_email(email)
            if not users:
                return None, "Usuário não encontrado. Por favor registre-se."
            cls._prefill_onboarding(users[0])
            return "/onboarding/step-1-personal", None
        except Exception as exc:  # pragma: no cover - guarded by tests on helpers
            logging.exception("Sign-in failed: %s", exc)
            return None, "Erro no login. Tente novamente."

    @rx.event
    async def signin(self, form_data: dict):
        redirect_to, error = await self._perform_signin(form_data)
        if error:
            yield rx.toast.error(error)
            return
        yield rx.redirect(redirect_to)
