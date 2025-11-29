import asyncio

from app.states.auth_state import AuthState
from app.states.onboarding_state import OnboardingState


def reset_onboarding_state() -> None:
    OnboardingState.current_step = 1
    OnboardingState.is_loading = False
    OnboardingState.personal_first_name = ""
    OnboardingState.personal_last_name = ""
    OnboardingState.personal_email = ""
    OnboardingState.personal_tax_number = ""
    OnboardingState.personal_birth_date = ""
    OnboardingState.personal_country = "Brasil"
    OnboardingState.personal_postal_code = ""
    OnboardingState.personal_house_number = ""
    OnboardingState.user_id = None
    OnboardingState.selected_plan = ""


class DummyClient:
    def __init__(self, users=None):
        self.users = users or []

    async def create_user(self, data):
        return [{"id": "user-1", **data}]

    async def get_user_by_email(self, email):
        return [user for user in self.users if user.get("email") == email]


def test_register_prefills_onboarding_and_redirects():
    reset_onboarding_state()
    client = DummyClient()
    redirect, error = asyncio.run(
        AuthState._perform_register(
            {
                "personal_first_name": "Ana",
                "personal_last_name": "Silva",
                "personal_email": "ana@boteco.pt",
                "password": "segura123",
                "personal_tax_number": "12345678901",
                "personal_postal_code": "12345678",
                "personal_house_number": "100",
            },
            client=client,
        )
    )

    assert error is None
    assert redirect == "/onboarding/step-1-personal"
    assert OnboardingState.personal_first_name == "Ana"
    assert OnboardingState.personal_last_name == "Silva"
    assert OnboardingState.personal_email == "ana@boteco.pt"
    assert OnboardingState.user_id == "user-1"
    assert OnboardingState.current_step == 1


def test_signin_loads_user_and_redirects():
    reset_onboarding_state()
    client = DummyClient(
        users=[
            {
                "id": "existing-1",
                "first_name": "Bruno",
                "last_name": "Souza",
                "email": "bruno@boteco.pt",
                "tax_number": "55555555555",
                "country": "Brasil",
            }
        ]
    )

    redirect, error = asyncio.run(
        AuthState._perform_signin({"email": "bruno@boteco.pt"}, client=client)
    )

    assert error is None
    assert redirect == "/onboarding/step-1-personal"
    assert OnboardingState.user_id == "existing-1"
    assert OnboardingState.personal_first_name == "Bruno"
    assert OnboardingState.personal_last_name == "Souza"
    assert OnboardingState.personal_email == "bruno@boteco.pt"


def test_signin_handles_missing_user():
    reset_onboarding_state()
    client = DummyClient(users=[])

    redirect, error = asyncio.run(
        AuthState._perform_signin({"email": "missing@boteco.pt"}, client=client)
    )

    assert redirect is None
    assert error == "Usuário não encontrado. Por favor registre-se."
    assert OnboardingState.user_id is None
