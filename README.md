# SmartRPA Monitor

Proyecto Full Stack inicial para monitoreo, autenticación y dashboard operativo de procesos RPA.

## Arquitectura

- `backend/`: API REST en Laravel 13 con Sanctum, capas `Controller -> Request -> Service -> Repository -> Model`.
- `frontend/`: React + Vite + TypeScript + Tailwind para login, layout privado, sidebar y dashboard.
- `RPAS/`: reservado para los procesos RPA locales.

## Requisitos previos

- PHP 8.3+
- Composer
- Node.js 20+
- PostgreSQL 15+

## Backend

1. Copia `backend/.env.example` a `backend/.env`
2. Configura PostgreSQL
3. Ejecuta:
   - `cd backend`
   - `composer install`
   - `php artisan key:generate`
   - `php artisan migrate --seed`
   - `php artisan serve`

### Variables importantes

- `DB_CONNECTION=pgsql`
- `DB_HOST=127.0.0.1`
- `DB_PORT=5432`
- `DB_DATABASE=smartrpa_monitor`
- `DB_USERNAME=postgres`
- `DB_PASSWORD=postgres`
- `ADMIN_NAME`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

### Endpoints disponibles

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/dashboard/summary`

### Credenciales iniciales

- Email: `admin@smartrpa.local`
- Password: `SmartRPA123*`

## Frontend

1. Copia `frontend/.env.example` a `frontend/.env`
2. Ejecuta:
   - `cd frontend`
   - `npm install`
   - `npm run dev`

### Variable importante

- `VITE_API_URL=http://localhost:8000/api`

## Pruebas

- Backend: `cd backend && php artisan test`
- Frontend build: `cd frontend && npm run build`

## Implementado en esta etapa

- Login, logout y persistencia de sesión
- Protección de rutas privadas
- Consulta del usuario autenticado
- Sidebar privada con logo SmartRPA
- Dashboard conectado a API real
- Seeders con roles, administrador y datos demo
- Migraciones base del modelo completo
- Pantallas base para módulos pendientes

## Pendiente para siguientes fases

- CRUD completos
- Detalle de ejecuciones/logs
- Gestión completa de incidentes
- Integración IA real
- Reportes avanzados
- Integración con agentes RPA locales
