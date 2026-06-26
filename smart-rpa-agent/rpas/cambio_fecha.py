def run(campus) -> dict:
    item = campus.cambiar_fecha()
    return {
        "rpa_code": "RPA-003",
        "message": f"Fechas actualizadas para {item['programa']}",
        "items": 1,
    }
