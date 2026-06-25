import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import WEB_DATA_PATH


class CampusSimulado:
    def __init__(self, data_path: Optional[Path] = None) -> None:
        self.data_path = data_path or WEB_DATA_PATH
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_path.exists():
            self._save(self._default_state())

    def registrar_resultados(self) -> Dict[str, Any]:
        state = self._load()
        item = self._take_first(state["pendientes"]["resultados"])
        if not item:
            raise ValueError("No hay resultados pendientes")
        item["estado"] = "procesado"
        state["resultados"].append(item)
        self._save(state)
        return item

    def publicar_certificado(self) -> Dict[str, Any]:
        state = self._load()
        item = self._take_first(state["pendientes"]["certificados"])
        if not item:
            raise ValueError("No hay certificados pendientes")
        item["estado"] = "publicado"
        state["certificados"].append(item)
        self._save(state)
        return item

    def cambiar_fecha(self) -> Dict[str, Any]:
        state = self._load()
        item = self._take_first(state["pendientes"]["fechas"])
        if not item:
            raise ValueError("No hay cambios de fecha pendientes")
        item["estado"] = "actualizado"
        state["fechas"].append(item)
        self._save(state)
        return item

    def crear_evaluacion(self) -> Dict[str, Any]:
        state = self._load()
        item = self._take_first(state["pendientes"]["evaluaciones"])
        if not item:
            raise ValueError("No hay evaluaciones pendientes")
        item["estado"] = "creado"
        state["evaluaciones"].append(item)
        self._save(state)
        return item

    def cambiar_nota(self) -> Dict[str, Any]:
        state = self._load()
        item = self._take_first(state["pendientes"]["notas"])
        if not item:
            raise ValueError("No hay cambios de nota pendientes")
        item["estado"] = "actualizado"
        state["notas"].append(item)
        self._save(state)
        return item

    def _load(self) -> Dict[str, Any]:
        return json.loads(self.data_path.read_text(encoding="utf-8"))

    def _save(self, state: Dict[str, Any]) -> None:
        self.data_path.write_text(json.dumps(state, indent=2, ensure_ascii=True), encoding="utf-8")

    def _take_first(self, items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return items.pop(0) if items else None

    def _default_state(self) -> Dict[str, Any]:
        return {
            "pendientes": {
                "resultados": [{"id": 1, "alumno": "Alumno 01", "curso": "Curso A", "nota": 18}],
                "certificados": [{"id": 1, "alumno": "Alumno 02", "programa": "Programa X"}],
                "fechas": [{"id": 1, "programa": "Programa Y", "fecha_inicio": "2026-07-01", "fecha_fin": "2026-07-30"}],
                "evaluaciones": [{"id": 1, "curso": "Curso B", "tipo": "Final"}],
                "notas": [{"id": 1, "alumno": "Alumno 03", "curso": "Curso C", "nota_actual": 12, "nota_nueva": 16}],
            },
            "resultados": [],
            "certificados": [],
            "fechas": [],
            "evaluaciones": [],
            "notas": [],
        }
