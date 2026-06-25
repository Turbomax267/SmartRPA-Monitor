# -*- coding: utf-8 -*-
import json
from resultado_rpa import ResultadoRPA
import cisam

def main(
    campus_conn=None,
    codigo_programa="",
    programa="",
    fecha_inicio_dice="",
    fecha_inicio_debe_decir="",
    fecha_fin_dice="",
    fecha_fin_debe_decir="",

    fecha_correo_ini_dice = "",
	fecha_correo_fin_dice = "",
	fecha_correo_ini_debe = "",
	fecha_correo_fin_debe = ""
):
    driver = None
    driver_original = None
    resultado_global = ResultadoRPA()
    ci = cisam.CisamConnect()
    ci.getConnection()

    try:
        if campus_conn is None:
            resultado_global.estado = 2
            resultado_global.error = 1
            resultado_global.continua = False
            resultado_global.mensaje_error = "Parámetros inválidos: campus_conn es requerido."
            return resultado_global

        if not str(programa or "").strip():
            print("[RPA][CAMBIO_FECHA] No hay solicitudes por procesar.")
            resultado_global.estado = 0
            resultado_global.error = 0
            resultado_global.continua = True
            return resultado_global

        print("[RPA][CAMBIO_FECHA] Solicitud a procesar:")
        print(
            {
                "codigo_programa": str(codigo_programa or "").strip(),
                "programa": str(programa or "").strip(),
                "fecha_inicio_dice": str(fecha_inicio_dice or "").strip(),
                "fecha_inicio_debe_decir": str(fecha_inicio_debe_decir or "").strip(),
                "fecha_fin_dice": str(fecha_fin_dice or "").strip(),
                "fecha_fin_debe_decir": str(fecha_fin_debe_decir or "").strip(),

                "fecha_correo_ini_dice": str(fecha_correo_ini_dice or "").strip(),
                "fecha_correo_fin_dice": str(fecha_correo_fin_dice or "").strip(),
                "fecha_correo_ini_debe": str(fecha_correo_ini_debe or "").strip(),
                "fecha_correo_fin_debe": str(fecha_correo_fin_debe or "").strip()
            }
        )

        driver = campus_conn.getDriver()
        driver_original = driver

        resultado_final = ResultadoRPA()
        codigo_programa_row = str(codigo_programa or "").strip()
        

        def _es_envio_confirmado(resultado):
            try:
                payload = json.loads(str(getattr(resultado, "mensaje_status", "") or ""))
                if isinstance(payload, dict):
                    status = str(payload.get("status", "") or "").strip().lower()
                    return status in ("submitted", "sent", "enviado")
            except Exception:
                pass
            return False

        try:
            programa_row = str(programa or "").strip()
            fecha_inicio_dice_row = str(fecha_inicio_dice or "").strip()
            fecha_inicio_debe_decir_row = str(fecha_inicio_debe_decir or "").strip()
            fecha_fin_dice_row = str(fecha_fin_dice or "").strip()
            fecha_fin_debe_decir_row = str(fecha_fin_debe_decir or "").strip()

            fecha_correo_ini_dice_row = str(fecha_correo_ini_dice or "").strip()
            fecha_correo_fin_dice_row = str(fecha_correo_fin_dice or "").strip()
            fecha_correo_ini_debe_row = str(fecha_correo_ini_debe or "").strip()
            fecha_correo_fin_debe_row = str(fecha_correo_fin_debe or "").strip()

            print("\n[RPA][CAMBIO_FECHA] ========================================")
            print("[RPA][CAMBIO_FECHA] Programa:", programa_row)

            resultado_final = campus_conn.cambiarFechasActividad(
                driver=driver,
                programa=programa_row,
                fecha_inicio_dice=fecha_inicio_dice_row,
                fecha_inicio_debe_decir=fecha_inicio_debe_decir_row,
                fecha_fin_dice=fecha_fin_dice_row,
                fecha_fin_debe_decir=fecha_fin_debe_decir_row,
                
                fecha_correo_ini_dice=fecha_correo_ini_dice_row,
                fecha_correo_fin_dice=fecha_correo_fin_dice_row,
                fecha_correo_ini_debe=fecha_correo_ini_debe_row,
                fecha_correo_fin_debe=fecha_correo_fin_debe_row
            )

        except Exception as e:
            msg = "Error inesperado en cambio de fecha: {}".format(e)
            print("[RPA][CAMBIO_FECHA][ERROR]", msg)
            resultado_final.estado = 2
            resultado_final.error = 1
            resultado_final.continua = False
            resultado_final.mensaje_error = msg

        finally:
            print("[RPA][CAMBIO_FECHA] Resultado estado=", getattr(resultado_final, "estado", 0))
            print("[RPA][CAMBIO_FECHA] Resultado error=", getattr(resultado_final, "error", 1))
            print(
                "[RPA][CAMBIO_FECHA] Resultado mensaje=",
                getattr(resultado_final, "mensaje_status", getattr(resultado_final, "mensaje_error", "")),
            )

            mensaje_log = str(
                getattr(resultado_final, "mensaje_error", "")
                or getattr(resultado_final, "mensaje_status", "")
                or ""
            )

            if _es_envio_confirmado(resultado_final):
                conf_cambiofecha = 2
            else:
                conf_cambiofecha = 0

            try:
                ci.registrarCambioFechasRpaLog(
                    codigo_programa=codigo_programa_row,
                    conf_cambiofecha=conf_cambiofecha,
                    mensaje=mensaje_log,
                )
            except Exception as e_log:
                print("[RPA][CAMBIO_FECHA][WARN] No se pudo registrar conf_cambiofecha:", e_log)
            finally:
                ci.closeConnection()

        resultado_global = resultado_final

        return resultado_global

    finally:
        try:
            if campus_conn is not None:
                campus_conn.closeCampusVirtual(driver=driver if driver is not None else driver_original)
        except Exception as e:
            print("[RPA][CAMBIO_FECHA][WARN] No se pudo cerrar Campus Virtual:", e)


if __name__ == "__main__":
    print(
        "[RPA][CAMBIO_FECHA] Uso: este módulo se ejecuta desde campus.py "
        "pasando parámetros a main(); la ejecución directa sin parámetros no está soportada."
    )
