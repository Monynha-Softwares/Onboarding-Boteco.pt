import reflex as rx
import reflex_clerk_api as clerk
import os
from app.pages.index import index
from app.pages.pricing import pricing
from app.pages.about import about
from app.pages.onboarding.personal import personal_step
from app.pages.onboarding.business import business_step
from app.pages.onboarding.plan import plan_step
from app.pages.onboarding.payment import payment_step
from app.pages.onboarding.success import success_page
from app.pages.dashboard import dashboard
from app.api.provision import api_app

app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap",
            rel="stylesheet",
        ),
    ],
    api_transformer=api_app,
)
app = clerk.wrap_app(
    app,
    publishable_key=os.getenv("CLERK_PUBLISHABLE_KEY"),
    secret_key=os.getenv("CLERK_SECRET_KEY"),
)
clerk.add_sign_in_page(app)
clerk.add_sign_up_page(app)
app.add_page(index, route="/")
app.add_page(pricing, route="/pricing")
app.add_page(about, route="/about")
app.add_page(personal_step, route="/onboarding/step-1-personal", on_load=clerk.protect)
app.add_page(business_step, route="/onboarding/step-2-business", on_load=clerk.protect)
app.add_page(plan_step, route="/onboarding/step-3-plan", on_load=clerk.protect)
app.add_page(payment_step, route="/onboarding/step-4-payment", on_load=clerk.protect)
app.add_page(success_page, route="/onboarding/success", on_load=clerk.protect)
app.add_page(dashboard, route="/app", on_load=clerk.protect)