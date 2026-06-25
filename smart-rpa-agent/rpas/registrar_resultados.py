def run(campus) -> dict:
    item = campus.registrar_resultados()
    return {
        "rpa_code": "RPA-003",
        "message": f"Resultado registrado para {item['alumno']}",
        "items": 1,
    }
