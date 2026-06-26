def run(campus) -> dict:
    item = campus.publicar_certificado()
    return {
        "rpa_code": "RPA-001",
        "message": f"Certificado publicado para {item['alumno']}",
        "items": 1,
    }
