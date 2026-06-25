def run(campus) -> dict:
    item = campus.crear_evaluacion()
    return {
        "rpa_code": "RPA-001",
        "message": f"Evaluacion creada para {item['curso']}",
        "items": 1,
    }
