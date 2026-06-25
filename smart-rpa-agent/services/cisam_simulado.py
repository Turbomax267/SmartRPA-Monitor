from services.campus_simulado import CampusSimulado


class CisamSimulado:
    def __init__(self, campus: CampusSimulado) -> None:
        self.campus = campus

    def obtener_pendientes(self):
        return self.campus._load()["pendientes"]
