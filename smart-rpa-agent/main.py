import argparse
import importlib
import time

from agent_state import AgentState
from api_client import ApiClient
from config import AGENT_NAME, POLL_INTERVAL
from reporter import get_logger
from services.campus_simulado import CampusSimulado
from services.cisam_simulado import CisamSimulado

RPA_MODULES = {
    "registrar_resultados": "rpas.registrar_resultados",
    "publicar_certificados": "rpas.publicar_certificados",
    "cambio_fecha": "rpas.cambio_fecha",
    "crear_evaluacion": "rpas.crear_evaluacion",
    "cambio_nota": "rpas.cambio_nota",
}

RPA_CODES = {
    "registrar_resultados": "RPA-003",
    "publicar_certificados": "RPA-002",
    "cambio_fecha": "RPA-004",
    "crear_evaluacion": "RPA-001",
    "cambio_nota": "RPA-005",
}

RPA_BY_CODE = dict((code, name) for name, code in RPA_CODES.items())


def execute_run_job(api, state, job, logger):
    rpa_code = job.get("rpaCode")
    rpa_name = RPA_BY_CODE.get(rpa_code)
    if not rpa_name:
        raise ValueError("No existe mapeo local para {}".format(rpa_code))

    if not state.is_enabled(rpa_code):
        raise ValueError("El RPA {} esta inactivo en local".format(rpa_code))

    campus = CampusSimulado()
    CisamSimulado(campus)
    module = importlib.import_module(RPA_MODULES[rpa_name])

    api.heartbeat(AGENT_NAME, "ONLINE", rpa_code)
    start = api.start_execution(rpa_code, rpa_name)
    execution_id = start["data"]["id"]

    try:
        result = module.run(campus)
        api.log(execution_id, "INFO", "RUN", result["message"], result)
        api.complete(
            execution_id,
            result["message"],
            total_items=result.get("items", 1),
            successful_items=result.get("items", 1),
            failed_items=0,
        )
        api.success_job(job["id"], execution_id=execution_id, result_message=result["message"], payload=result)
        logger.info(result["message"])
    except Exception as exc:
        error_message = str(exc)
        api.log(execution_id, "ERROR", "RUN", error_message, {"rpa": rpa_name})
        api.fail(execution_id, "SIM_ERROR", error_message, "Simulado")
        api.fail_job(job["id"], error_message=error_message, execution_id=execution_id, payload={"rpa": rpa_name})
        raise
    finally:
        api.heartbeat(AGENT_NAME, "ONLINE")


def execute_state_job(api, state, job, enabled, logger):
    rpa_code = job.get("rpaCode")
    if not rpa_code:
        raise ValueError("El job no tiene rpaCode")

    state.set_enabled(rpa_code, enabled)
    message = "RPA {} {}".format(rpa_code, "activado" if enabled else "desactivado")
    api.success_job(job["id"], result_message=message, payload={"enabled": enabled, "rpa_code": rpa_code})
    logger.info(message)


def process_job(api, state, job, logger):
    api.take_job(job["id"])
    api.running_job(job["id"])

    command = job.get("command")
    if command == "activate":
        execute_state_job(api, state, job, True, logger)
        return

    if command == "deactivate":
        execute_state_job(api, state, job, False, logger)
        return

    if command == "run":
        execute_run_job(api, state, job, logger)
        return

    raise ValueError("Comando no soportado: {}".format(command))


def worker():
    logger = get_logger("worker")
    api = ApiClient()
    state = AgentState()

    logger.info("Worker iniciado con polling cada %ss", POLL_INTERVAL)

    while True:
        try:
            api.heartbeat(AGENT_NAME, "ONLINE")
            response = api.next_job()
            job = response.get("data")

            if not job:
                time.sleep(POLL_INTERVAL)
                continue

            if job.get("command") == "run" and not state.is_enabled(job.get("rpaCode")):
                logger.info("Job %s en espera: %s no esta habilitado localmente", job.get("id"), job.get("rpaCode"))
                time.sleep(POLL_INTERVAL)
                continue

            logger.info("Job recibido %s %s", job.get("id"), job.get("command"))
            process_job(api, state, job, logger)
        except Exception as exc:
            logger.exception("Error en worker: %s", exc)
            time.sleep(POLL_INTERVAL)


def run_once(name):
    api = ApiClient()
    state = AgentState()
    logger = get_logger(name)
    state.set_enabled(RPA_CODES[name], True)
    rpa_code = RPA_CODES[name]
    campus = CampusSimulado()
    CisamSimulado(campus)
    module = importlib.import_module(RPA_MODULES[name])

    api.heartbeat(AGENT_NAME, "ONLINE", rpa_code)
    start = api.start_execution(rpa_code, name)
    execution_id = start["data"]["id"]

    try:
        result = module.run(campus)
        api.log(execution_id, "INFO", "RUN", result["message"], result)
        api.complete(
            execution_id,
            result["message"],
            total_items=result.get("items", 1),
            successful_items=result.get("items", 1),
            failed_items=0,
        )
        logger.info(result["message"])
    except Exception as exc:
        error_message = str(exc)
        api.log(execution_id, "ERROR", "RUN", error_message, {"rpa": name})
        api.fail(execution_id, "SIM_ERROR", error_message, "Simulado")
        raise
    finally:
        api.heartbeat(AGENT_NAME, "ONLINE")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["worker"] + list(RPA_MODULES.keys()) + ["all"])
    args = parser.parse_args()

    if args.mode == "worker":
        worker()
        return

    if args.mode == "all":
        for name in RPA_MODULES:
            run_once(name)
        return

    run_once(args.mode)


if __name__ == "__main__":
    main()
