# BotecoPro Onboarding

BotecoPro é uma experiência completa de onboarding para bares e restaurantes que usam a plataforma desenvolvida pela Monynha Softwares. O app conduz novas contas desde a criação de usuário até a configuração inicial do estabelecimento, incluindo coleta de dados pessoais, informações do negócio, escolha de plano e simulação de pagamento. Todo o fluxo é construído em Reflex com estilização Tailwind e integrações com Supabase e Clerk.

## Visão Geral do Fluxo
- **Cadastro e login personalizados:** telas de signup/signin próprias preenchem o estado de onboarding antes de redirecionar para os passos.
- **Passo a passo guiado:** dados pessoais → dados do negócio → escolha de plano → pagamento/sucesso.
- **Provisionamento remoto:** o passo final dispara uma chamada interna para provisionar schema dedicado no Supabase.
- **Dashboard inicial:** após o sucesso, o usuário pode acessar um dashboard placeholder protegido via Clerk.

## Stack Técnica
- **Backend/UI:** [Reflex](https://reflex.dev) (Python) com componentes estilizados via Tailwind classes.
- **Autenticação:** Clerk (via `reflex-clerk-api`) para proteger rotas e gerenciar sessão.
- **Banco e APIs:** Supabase para persistência de usuários/botecos e RPC de provisionamento.
- **Infra adicional:** FastAPI para o endpoint interno `/api/provision_org`.
- **Testes:** Pytest.

## Requisitos
- Python 3.11+
- Node/Tailwind não são necessários para rodar o app; o plugin Tailwind do Reflex já é aplicado em build.
- Variáveis de ambiente configuradas (veja abaixo).

## Variáveis de Ambiente
Defina as chaves sensíveis antes de rodar:

| Variável | Descrição |
| --- | --- |
| `SUPABASE_URL` | URL do projeto Supabase. |
| `SUPABASE_KEY` | Chave pública do Supabase (fallback quando a service role não estiver disponível). |
| `SUPABASE_SERVICE_ROLE_KEY` | Chave service role para operações administrativas e RPC de provisionamento. |
| `CLERK_PUBLISHABLE_KEY` | Publishable key do projeto Clerk. |
| `CLERK_SECRET_KEY` | Secret key do projeto Clerk. |

## Instalação
```bash
pip install -r requirements.txt
```

## Executando em Desenvolvimento
```bash
reflex run
```
Isso inicia o app Reflex e expõe a API interna de provisionamento. Certifique-se de ter as variáveis de ambiente carregadas para que Supabase e Clerk funcionem corretamente.

## Testes
```bash
pytest -q
```

## Build e Deploy
1. Gere os assets de produção:
   ```bash
   reflex export --frontend-only
   ```
2. Suba o backend (API de provisionamento) com o servidor de sua preferência apontando para o módulo `app.api.provision:api_app` se usar Uvicorn/Gunicorn.
3. Garanta que as variáveis de ambiente de Supabase e Clerk estejam disponíveis no ambiente de produção.

## Estrutura do Projeto
- `app/app.py`: configuração do app, páginas registradas e metatags.
- `app/pages/`: páginas públicas, autenticação e onboarding.
- `app/states/`: estados globais (`AuthState`, `OnboardingState`, `BaseState`).
- `app/services/`: client helper para Supabase e API interna de provisionamento.
- `app/components/`: cabeçalho, rodapé e stepper reutilizáveis.
- `assets/`: ícones e imagens estáticas.
- `tests/`: suíte Pytest cobrindo fluxo de autenticação e branding.
