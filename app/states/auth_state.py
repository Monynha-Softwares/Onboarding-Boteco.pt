import reflex as rx
import logging
from app.services.supabase_client import supabase_client
from app.states.onboarding_state import OnboardingState


class AuthState(rx.State):
    """Custom auth state to register/sign-in users into onboarding flow.

    Note: this project previously relied on Clerk for auth. The original Clerk
    integration is left in the repo (commented in `app/app.py`) but this
    state provides a minimal custom flow that persists the user's personal
    details into Supabase and redirects them into onboarding.
    """

    @rx.event
    async def register(self, form_data: dict):
        """Register a new personal account and start onboarding.

        Expects same fields as the personal onboarding form. Persists a user
        record in Supabase via `supabase_client.upsert_user` and then
        redirects to the onboarding flow. Also attempts to populate
        `OnboardingState` fields so the onboarding form is prefilled.
        """
        first_name = form_data.get("personal_first_name", "")
        last_name = form_data.get("personal_last_name", "")
        email = form_data.get("personal_email", "")
        tax_number = form_data.get("personal_tax_number", "")
        birth_date = form_data.get("personal_birth_date", "")
        country = form_data.get("personal_country", "Brasil")
        postal_code = form_data.get("personal_postal_code", "")
        house_number = form_data.get("personal_house_number", "")

        if not all([first_name, last_name, email]):
            yield rx.toast.error("Por favor, preencha nome e email.")
            return

        user_data = {
            "email": email,
            "username": f"{first_name.lower()}.{last_name.lower()}{tax_number[:4]}",
            "tax_number": tax_number,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "country": country,
            "postal_code": postal_code,
            "house_number": house_number,
            "is_owner": True,
        }

        try:
            response = await supabase_client.upsert_user(user_data)
            if response.data:
                created_user = response.data[0]
                # Try to populate onboarding state defaults so the form is prefilled
                OnboardingState.personal_first_name = created_user.get("first_name", "")
                OnboardingState.personal_last_name = created_user.get("last_name", "")
                OnboardingState.personal_email = created_user.get("email", "")
                OnboardingState.personal_tax_number = created_user.get("tax_number", "")
                OnboardingState.personal_birth_date = created_user.get("birth_date", "")
                OnboardingState.personal_country = created_user.get("country", "Brasil")
                OnboardingState.personal_postal_code = created_user.get("postal_code", "")
                OnboardingState.personal_house_number = created_user.get("house_number", "")
                OnboardingState.user_id = created_user.get("id")
                # Start onboarding at step 1 (personal) so user can continue the flow
                yield rx.redirect("/onboarding/step-1-personal")
                return
            else:
                raise Exception(response.error.message if response.error else "No data returned")
        except Exception as e:
            logging.exception(f"Failed to register user: {e}")
            yield rx.toast.error(f"Falha ao criar conta: {e}")

    @rx.event
    async def signin(self, form_data: dict):
        """Sign-in by email: if a user exists, set onboarding `user_id` and redirect.

        This is intentionally minimal: it does not implement passwords. It's
        useful for dev/demo workflows where Supabase is the canonical user store.
        """
        email = form_data.get("email", "")
        if not email:
            yield rx.toast.error("Forneça um email para entrar.")
            return
        try:
            user = await supabase_client.get_user_by_email(email)
            if user and len(user) > 0:
                u = user[0]
                OnboardingState.user_id = u.get("id")
                OnboardingState.personal_first_name = u.get("first_name", "")
                OnboardingState.personal_last_name = u.get("last_name", "")
                OnboardingState.personal_email = u.get("email", "")
                yield rx.redirect("/onboarding/step-1-personal")
                return
            else:
                yield rx.toast.error("Usuário não encontrado. Por favor registre-se.")
                return
        except Exception as e:
            logging.exception(f"Sign-in failed: {e}")
            yield rx.toast.error("Erro no login. Tente novamente.")
            return
