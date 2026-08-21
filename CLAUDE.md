# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Estado del proyecto

Monorepo **IntegraTrip** (tarea T1 de IIC3103) recién inicializado: solo el scaffolding y las carpetas vacías. No hay lógica de negocio todavía — el único endpoint es `GET /health`. Las carpetas de capas existen con `.gitkeep` / `__init__.py` vacíos, esperando código.

No es un repositorio git.

## Comandos

Frontend (`frontend/`):

```bash
npm install
npm run dev      # Vite dev server
npm run build    # tsc -b && vite build
npm run lint     # oxlint
```

Backend (`backend/`):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

No hay tests configurados en ninguno de los dos lados.

### Nota sobre `npm install` en este entorno (WSL2)

Un `npm install` que "se cuelga eternamente" y no responde a Ctrl+C suele ser **dos `npm install` simultáneos** sobre el mismo `node_modules` (por ejemplo uno dejado en background). Diagnóstico y arreglo:

```bash
pgrep -af "npm install"        # si hay más de uno, están colisionando
kill -9 <pid>                  # Ctrl+C no sirve si el proceso perdió su terminal
rm -rf node_modules package-lock.json && npm install
```

Una instalación limpia toma ~5 s. Nunca lances un `npm install` en background aquí y luego otro en foreground.

## Arquitectura prevista

IntegraTrip es un **cliente MCP**: el usuario se autentica, conecta tres servidores MCP externos, lista sus tools y las ejecuta. Cada servidor usa un esquema OAuth distinto — esa es la complejidad central del proyecto:

| Servidor MCP | Dominio | Auth | Cómo se obtiene el `client_id` |
|---|---|---|---|
| Andes Air | vuelos | PRE | registro manual previo en el AS, credenciales fijas en env vars |
| StayWell | hoteles | DCR | `POST` al endpoint de registro del AS durante el flujo |
| Cielo Sur | clima | CIMD | el `client_id` es una URL pública que expone el backend (`/.well-known/oauth-client`) |

Los tres comparten el mismo esqueleto Authorization Code + PKCE; solo cambia cómo se establece el cliente antes del flujo. El login del usuario en la app propia usa el mismo mecanismo que PRE.

**Componentes**: SPA React/Vite (Vercel) → API HTTP con cookie de sesión `httpOnly` → backend FastAPI (Railway) → Supabase (Postgres) y el Authorization Server externo del curso.

**Invariante de seguridad**: el backend es el único componente que conoce credenciales. El frontend nunca recibe `client_secret`, `access_token` ni `refresh_token` de ningún MCP; solo la cookie de sesión de la app (`httpOnly`, `Secure`, `SameSite=None`, porque frontend y backend viven en dominios distintos). Los tokens se guardan cifrados en Supabase con clave en variable de entorno.

### Capas

`backend/app/`: `routers/` (endpoints HTTP) · `services/` (lógica de negocio, un módulo OAuth por tipo) · `models/` (dominio) · `schemas/` (contratos Pydantic) · `db/` (acceso a Supabase) · `security/` (cifrado de tokens, sesión).

`frontend/src/`: `api/` · `pages/` · `components/` · `types/`.

Esta separación existe para que la siguiente tarea (incorporar un LLM) agregue un router/servicio de "agente" sin tocar la lógica de conexión MCP.

### Modelo de datos previsto

Cuatro tablas: `users` (guarda el `sub` del AS, sin contraseñas propias) · `mcp_servers` (config de los 3 servidores, a nivel de app, con campos de cliente que varían según `auth_type`) · `mcp_connections` (tabla puente usuario↔servidor con los tokens cifrados, `UNIQUE(user_id, mcp_server_id)`) · `oauth_flow_state` (`state` anti-CSRF y `code_verifier` de PKCE, temporal, se limpia por `expires_at`).

## Convenciones

Variables de entorno: `frontend/.env.example` (`VITE_API_BASE_URL`) y `backend/.env.example` (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SESSION_SECRET_KEY`). Los `.env` reales están en `.gitignore`.

No agregar dependencias fuera de las ya listadas sin que el usuario lo pida.

## Restricción del curso

El **informe de arquitectura oficial** (`docs/`, incluye el modelo Entidad-Relación) **no puede ser redactado con IA** según el enunciado. Los documentos de diseño generados con Claude son borradores de trabajo, no el entregable — no escribas el informe final por el usuario.
