import reflex as rx
from app.states.auth_state import AuthState
from app.components.onboarding_stepper import onboarding_stepper


def form_field(label: str, placeholder: str, value: rx.Var, on_change: rx.event.EventHandler, name: str, field_type: str = "text") -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-[#4F3222]"),
        rx.el.input(
            placeholder=placeholder,
            on_change=on_change,
            name=name,
            type=field_type,
            class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#B3701A] focus:border-[#B3701A] sm:text-sm",
            default_value=value,
        ),
        class_name="col-span-6 sm:col-span-3",
    )


def signup_page() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    "Boteco.pt",
                    href="/",
                    class_name="text-2xl font-bold text-[#8B1E3F] hover:opacity-90 transition-opacity",
                ),
                class_name="py-8 px-4 sm:px-6 lg:px-8 bg-[#F1DDAD]/50 border-b border-gray-200",
            ),
            onboarding_stepper(rx.var(0)),
            rx.el.div(
                rx.el.h2("Criar Conta", class_name="text-2xl font-bold text-[#4F3222]"),
                rx.el.p(
                    "Crie sua conta pessoal para começar o onboarding.",
                    class_name="mt-2 text-sm text-[#4F3222]/80",
                ),
                rx.el.form(
                    rx.el.div(
                        form_field(
                            "Nome",
                            "",
                            rx.var("") ,
                            AuthState.set_personal_first_name if hasattr(AuthState, 'set_personal_first_name') else (lambda *_: None),
                            name="personal_first_name",
                        ),
                        form_field(
                            "Sobrenome",
                            "",
                            rx.var("") ,
                            AuthState.set_personal_last_name if hasattr(AuthState, 'set_personal_last_name') else (lambda *_: None),
                            name="personal_last_name",
                        ),
                        form_field(
                            "Email",
                            "",
                            rx.var("") ,
                            AuthState.set_personal_email if hasattr(AuthState, 'set_personal_email') else (lambda *_: None),
                            name="personal_email",
                            field_type="email",
                        ),
                        form_field(
                            "CPF",
                            "",
                            rx.var("") ,
                            AuthState.set_personal_tax_number if hasattr(AuthState, 'set_personal_tax_number') else (lambda *_: None),
                            name="personal_tax_number",
                        ),
                        form_field(
                            "Data de Nascimento",
                            "",
                            rx.var("") ,
                            AuthState.set_personal_birth_date if hasattr(AuthState, 'set_personal_birth_date') else (lambda *_: None),
                            name="personal_birth_date",
                            field_type="date",
                        ),
                        form_field(
                            "CEP",
                            "",
                            rx.var("") ,
                            AuthState.set_personal_postal_code if hasattr(AuthState, 'set_personal_postal_code') else (lambda *_: None),
                            name="personal_postal_code",
                        ),
                        form_field(
                            "Número da Casa/Apto",
                            "",
                            rx.var("") ,
                            AuthState.set_personal_house_number if hasattr(AuthState, 'set_personal_house_number') else (lambda *_: None),
                            name="personal_house_number",
                        ),
                        class_name="grid grid-cols-6 gap-6 mt-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Criar Conta e Iniciar Onboarding",
                            type="submit",
                            class_name="inline-flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#8B1E3F] hover:bg-[#7a1a37]",
                        ),
                        class_name="flex justify-end mt-8",
                    ),
                    on_submit=AuthState.register,
                ),
                class_name="max-w-2xl mx-auto p-8 bg-white rounded-xl shadow-md border border-gray-200/80",
            ),
            class_name="pb-16",
        ),
        class_name="min-h-screen bg-[#F1DDAD]/30 font-['Inter']",
    )
