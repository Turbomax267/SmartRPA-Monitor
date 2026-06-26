# Flujo de agentes RPA

Este proyecto ya tiene la base lista para trabajar con agentes locales que:

- envían `heartbeat` al backend
- consultan jobs pendientes
- toman el job
- ejecutan el RPA
- registran ejecución, logs, éxito o fallo en la misma base de datos

## Cómo funciona

### 1. Desde la web

En `RPA / Bots`:

- `Ejecutar` crea un job `run`
- `Activar` crea un job `activate`
- `Desactivar` crea un job `deactivate`

Eso pega a:

- `POST /api/jobs`

Backend involucrado:

- `backend/app/Http/Controllers/Api/RpaJobController.php`

### 2. Desde el agente local

El agente está en:

- `smart-rpa-agent/`

El worker:

- hace `heartbeat`
- consulta `GET /api/agent/jobs/next`
- toma el job
- lo marca `running`
- ejecuta el RPA
- registra logs y ejecución
- marca el job como `success` o `fail`

Archivo principal:

- `smart-rpa-agent/main.py`

## Variables del agente

Crea o ajusta:

- `smart-rpa-agent/.env`

Ejemplo:

```env
SMART_RPA_API_URL=http://localhost:8000/api
SMART_RPA_AGENT_TOKEN=agent-lima-01-token
AGENT_NAME=AGENT-LIMA-01
SMART_RPA_TIMEOUT=30
SMART_RPA_POLL_INTERVAL=5
```

En Render, si quieres apuntar al backend desplegado:

```env
SMART_RPA_API_URL=https://smartrpa-monitor-backend.onrender.com/api
SMART_RPA_AGENT_TOKEN=agent-lima-01-token
AGENT_NAME=AGENT-LIMA-01
SMART_RPA_TIMEOUT=30
SMART_RPA_POLL_INTERVAL=5
```

## Cómo levantar el agente en local

Desde la raíz del repo:

```bat
cd smart-rpa-agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py worker
```

## Ejecutar un RPA puntual

También puedes probar uno específico:

```bat
cd smart-rpa-agent
.venv\Scripts\activate
python main.py cambio_fecha
python main.py cambio_nota
python main.py crear_evaluacion
python main.py publicar_certificados
python main.py registrar_resultados
```

## Mapeo actual de RPAs

Según `smart-rpa-agent/main.py`:

- `RPA-001` → `crear_evaluacion`
- `RPA-002` → `publicar_certificados`
- `RPA-003` → `registrar_resultados`
- `RPA-004` → `cambio_fecha`
- `RPA-005` → `cambio_nota`

## Qué debes validar en base de datos

Para que el flujo funcione bien:

- `rpa_agents.code` debe coincidir con `AGENT_NAME`
- `rpa_agents.api_key_hash` debe corresponder al token real del agente
- `rpas.default_agent_id` debe apuntar a un agente existente
- `rpa_jobs` debe existir
- `personal_access_tokens` debe existir para login web

## Flujo recomendado de operación

1. Levanta backend
2. Levanta frontend
3. Levanta `smart-rpa-agent` en modo `worker`
4. Desde la web entra a `RPA / Bots`
5. Usa `Ejecutar`, `Activar` o `Desactivar`
6. El agente tomará el job en el siguiente polling
7. Revisa:
   - `Ejecuciones`
   - `Logs`
   - `Alertas`
   - `Análisis IA`

## Nota importante

Hoy el backend ya soporta:

- jobs
- heartbeats
- creación de ejecuciones
- logs
- completar/fallar ejecuciones
- activar/desactivar RPAs por job

Si luego quieres, el siguiente paso natural es agregar en la web:

- panel de jobs en tiempo real
- estado por agente
- última señal heartbeat por tarjeta
- cancelación manual de jobs pendientes
