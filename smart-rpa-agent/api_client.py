from datetime import datetime
from typing import Any, Dict, Optional

import requests
from requests import HTTPError

from config import REQUEST_TIMEOUT, SMART_RPA_AGENT_TOKEN, SMART_RPA_API_URL


class ApiClient:
    def __init__(self) -> None:
        self.base_url = SMART_RPA_API_URL.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {SMART_RPA_AGENT_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def heartbeat(self, agent_code: str, status: str, current_rpa: Optional[str] = None) -> Dict[str, Any]:
        return self._post(
            "/agent/heartbeat",
            {
                "agent_code": agent_code,
                "status": status,
                "current_rpa": current_rpa,
                "sent_at": datetime.now().astimezone().isoformat(),
            },
        )

    def next_job(self):
        response = requests.get(
            f"{self.base_url}/agent/jobs/next",
            headers=self.headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def take_job(self, job_id):
        return self._post("/agent/jobs/{}/take".format(job_id), {})

    def running_job(self, job_id):
        return self._post("/agent/jobs/{}/running".format(job_id), {})

    def success_job(self, job_id, execution_id=None, result_message="", payload=None):
        return self._post(
            "/agent/jobs/{}/success".format(job_id),
            {
                "execution_id": execution_id,
                "result_message": result_message,
                "payload": payload or {},
            },
        )

    def fail_job(self, job_id, error_message, execution_id=None, payload=None):
        return self._post(
            "/agent/jobs/{}/fail".format(job_id),
            {
                "execution_id": execution_id,
                "error_message": error_message,
                "payload": payload or {},
            },
        )

    def start_execution(self, rpa_code: str, scenario: str = "General") -> Dict[str, Any]:
        return self._post(
            "/agent/executions/start",
            {
                "rpa_code": rpa_code,
                "trigger_type": "API",
                "scenario": scenario,
            },
        )

    def log(self, execution_id: int, level: str, step: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._post(
            f"/agent/executions/{execution_id}/logs",
            {
                "level": level,
                "step": step,
                "message": message,
                "context": context or {},
            },
        )

    def complete(self, execution_id: int, result_summary: str, total_items: int = 1, successful_items: int = 1, failed_items: int = 0) -> Dict[str, Any]:
        return self._post(
            f"/agent/executions/{execution_id}/complete",
            {
                "result_summary": result_summary,
                "total_items": total_items,
                "successful_items": successful_items,
                "failed_items": failed_items,
            },
        )

    def fail(
        self,
        execution_id: int,
        error_code: str,
        error_message: str,
        category: str = "General",
        total_items: int = 1,
        successful_items: int = 0,
        failed_items: int = 1,
    ) -> Dict[str, Any]:
        return self._post(
            f"/agent/executions/{execution_id}/fail",
            {
                "error_code": error_code,
                "error_message": error_message,
                "category": category,
                "severity": "HIGH",
                "result_summary": error_message,
                "total_items": total_items,
                "successful_items": successful_items,
                "failed_items": failed_items,
            },
        )

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}{path}",
            json=payload,
            headers=self.headers,
            timeout=REQUEST_TIMEOUT,
        )

        try:
            response.raise_for_status()
        except HTTPError as exc:
            body = response.text.strip()
            message = f"{exc} | response: {body}" if body else str(exc)
            raise HTTPError(message, response=response) from exc

        return response.json()
