# Barnostri Platform Implementation Plan

## Overview
Building institutional + onboarding platform for Boteco Pro system using Reflex, Clerk, Supabase, and simulated Stripe checkout.

**Theme**: Wine (#8B1E3F) + Mustard (#B3701A) with Material Design 3.0

---

## Phase 1: Project Setup + Public Marketing Pages ✅
- [x] Setup project structure (pages/, components/, services/, utils/)
- [x] Create Supabase client helper with connection utilities
- [x] Build landing page (/) with hero section, CTA, how it works, plans preview, about preview
- [x] Build pricing page (/pricing) with detailed plan cards (boteco, boteco_pro, boteco_patrao, boteco_babadeiro)
- [x] Build about page (/about) with company info and mission
- [x] Create shared header component with navigation and auth buttons
- [x] Create shared footer component with links and branding
- [x] Apply Barnostri theme colors throughout (Wine primary, Mustard secondary, Beige/Brown accents)

---

## Phase 2: Clerk Authentication + Onboarding Flow UI ✅
- [x] Integrate Clerk authentication with app wrapper and user state registration
- [x] Build /app dashboard with redirect logic to onboarding if no org
- [x] Build /onboarding/step-1-personal with personal data form (prefilled from Clerk, tax_number, birth_date, address fields)
- [x] Build /onboarding/step-2-business with business registration form (name, username, category, tax_number, location, vibe tags)
- [x] Build /onboarding/step-3-plan with plan selection cards and comparison
- [x] Build /onboarding/step-4-payment with simulated Stripe-like checkout UI
- [x] Build /onboarding/success with welcome message and panel link
- [x] Create progress stepper component showing steps 1-4
- [x] Add form validation, error handling, and loading states

---

## Phase 3: Supabase Integration + Backend Logic ✅
- [x] Implement user data persistence - insert/upsert to public.users after step 1
- [x] Implement business data persistence - insert to public.boteco after payment success
- [x] Implement user-boteco association - insert to public.user_boteco with plan and role
- [x] Create backend endpoint /api/provision_org for schema provisioning using service role key
- [x] Build payment success handler with transaction (boteco + user_boteco insert + provisioning trigger)
- [x] Add onboarding state management for multi-step flow with data persistence
- [x] Implement redirect logic and completion checks
- [x] Add error handling and rollback for failed transactions

---

## Phase 4: UI Verification & Testing ✅
- [x] Test landing page - verified hero section, CTA buttons, how it works cards, plans preview, footer navigation all render correctly
- [x] Test pricing page - verified all 4 plan cards with proper visual hierarchy, recommended plan stands out, comparison table displays correctly
- [x] Test about page - verified mission section, values cards with icons, team member initials placeholders, CTA section with proper contrast
- [x] Test responsive design - verified mobile navigation (hamburger menu), desktop navigation (hidden on mobile), proper breakpoints working
- [x] Enhanced visual hierarchy - improved recommended plan card styling, better placeholder handling for team photos, proper color theming throughout