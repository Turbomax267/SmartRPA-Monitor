import pyodbc
import pandas as pd
import numpy as np
import time
import configparser
config = configparser.ConfigParser()
config.read('/var/www/my_config_rpa.cnf')
class CisamConnect():

	def __init__(self, **kwargs):
		self.username = config['cisam']['username']
		self.password = config['cisam']['password']
		self.host = config['cisam']['host']
		self.port = config['cisam']['port']
		self.database = config['cisam']['database']
		self.driver = 'ODBC Driver 17 for SQL Server'
		self.conn = None

        
	def getConnection(self):
		cadena_con = 'DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'\
               .format(self.driver,self.host, self.database, self.username,self.password)
        
		self.conn = pyodbc.connect(cadena_con, autocommit=True)
    
	def closeConnection(self):
		self.conn.close()

	def getPagoRaesNg(self):
		query= '''
			SELECT 
			  mcp.id
			  ,mcp.id_programa
			  ,mcp.id_seccion
			  ,mcp.id_asignatura
				,cm.nombre as nombre_asignatura
			  ,sp.nombre_programa
			  ,[fecha_inicio_horario]
			  ,[fecha_fin_horario]
			  ,(SELECT 
			      top 1 us.[data]
			  FROM user_detail as us
			  where us.user_id = mtp.id_teacher
			  and us.fieldid = 423) as codigo_teacher
			  ,mpd.id as id_detalle
			  ,mpd.mensaje_validaciones
			  ,mpd.raes_json
			  ,j.[key] as mes_procesar
			  ,(
				SELECT
				 sum(DATEDIFF(minute,scsh.[fecha_inicio],scsh.[fecha_final]))*1.0/60.0
				FROM schedule_cal_sesion_history as scsh
				where scsh.id_programa = mcp.id_programa
				and scsh.id_seccion = mcp.id_seccion
				and scsh.id_course = mcp.id_asignatura
				and scsh.id_teacher = mtp.id_teacher
				and scsh.estado = '1'
				and left(scsh.fecha_inicio_html,7) = CONCAT(JSON_VALUE(j.value, '$.anho'),'-',CONCAT('0',j.[key])) COLLATE Modern_Spanish_CI_AS
			  ) as total_horas
			  ,JSON_VALUE(raes_json, concat('$."',j.[key] COLLATE Modern_Spanish_CI_AS,'".anho')) as anho
			FROM manage_pago_curso_programa as mcp 
			join manage_pago_curso_teacher_programa as mtp on mtp.id_programa_curso = mcp.id
			JOIN manage_pago_curso_proceso_detalle as mpd ON mpd.id_teacher_programa = mtp.id 
			JOIN manage_pago_curso_proceso as mpp ON mpp.id = mpd.id_curso_proceso
			join schedule_program as sp on sp.id_program = mcp.id_programa
			left join curso_malla as cm on cm.cod_curso = mcp.id_asignatura and cm.id_malla = sp.id_malla
			CROSS APPLY OPENJSON(mpd.raes_json) as j
			where mcp.estado = '1'
			  AND mpd.estado = '3' 
			  AND mpd.estado_curso = '8'
			  AND mpp.estado = '3'
			  AND mpd.cierre_manual in ('0','2')
			  AND mpd.raes_json IS NOT NULL
			  AND JSON_VALUE(mpd.raes_json, '$."' + j.[key] + '".estado') COLLATE SQL_Latin1_General_CP1_CI_AS IN ('1', '2')
				--AND mpd.id IN  ('37', '39', '43', '51', '52')
    '''
		return pd.read_sql(query, con=self.conn)
	
	def actualizar_raes_json(self, id_detalle, raes_json):
		cursor = self.conn.cursor()
		query = """
			UPDATE manage_pago_curso_proceso_detalle
			SET raes_json = ?
			WHERE id = ?
		"""
		cursor.execute(query, (raes_json, id_detalle))
		self.conn.commit()
		return True
		
	def getPagoRaesNgEstado3(self):
		query ="""
			SELECT 
			  mcp.id
			  ,mcp.id_programa
			  ,mcp.id_seccion
			  ,mcp.id_asignatura
			  ,sp.nombre_programa
			  ,cm.nombre as nombre_asignatura
			  ,[fecha_inicio_horario]
			  ,[fecha_fin_horario]
			  ,(SELECT 
			    top 1 us.[data]
			  FROM user_detail as us
			  where us.user_id = mtp.id_teacher
			  and us.fieldid = 423) as codigo_teacher
			  ,mpd.id as id_detalle
			  ,mpd.mensaje_validaciones
			  ,mpd.raes_json
			  ,j.[key] as mes_procesar
			FROM manage_pago_curso_programa as mcp 
			join manage_pago_curso_teacher_programa as mtp on mtp.id_programa_curso = mcp.id
			JOIN manage_pago_curso_proceso_detalle as mpd ON mpd.id_teacher_programa = mtp.id 
			JOIN manage_pago_curso_proceso as mpp ON mpp.id = mpd.id_curso_proceso
			join schedule_program as sp on sp.id_program = mcp.id_programa
			left join curso_malla as cm on cm.cod_curso = mcp.id_asignatura and cm.id_malla = sp.id_malla
			CROSS APPLY OPENJSON(mpd.raes_json) as j
			where mcp.estado = '1'
			  AND mpd.estado = '3' 
			  AND mpd.estado_curso = '8'
			  AND mpp.estado = '3'
			  AND mpd.cierre_manual in ('0','2')
			  AND mpd.raes_json IS NOT NULL
			  AND JSON_VALUE(mpd.raes_json, '$."' + j.[key] + '".estado') COLLATE DATABASE_DEFAULT in ('3','4')
				--AND mpd.id IN  ('37', '39', '43', '51', '52')
		"""
		return pd.read_sql(query, con=self.conn)
	
	def getPagoRaesNgEstado5(self):
		query="""
			SELECT 
				mcp.id
				,mcp.id_programa
				,mcp.id_seccion
				,mcp.id_asignatura
				,sp.nombre_programa
				,cm.nombre as nombre_asignatura
				,[fecha_inicio_horario]
				,[fecha_fin_horario]
				,(SELECT 
				top 1 us.[data]
				FROM user_detail as us
				where us.user_id = mtp.id_teacher
				and us.fieldid = 423) as codigo_teacher
				,mpd.id as id_detalle
				,mpd.raes_json
				,j.[key] as mes_procesar
			FROM manage_pago_curso_programa as mcp 
			join manage_pago_curso_teacher_programa as mtp on mtp.id_programa_curso = mcp.id
			JOIN manage_pago_curso_proceso_detalle as mpd ON mpd.id_teacher_programa = mtp.id 
			JOIN manage_pago_curso_proceso as mpp ON mpp.id = mpd.id_curso_proceso
			join schedule_program as sp on sp.id_program = mcp.id_programa
			left join curso_malla as cm on cm.cod_curso = mcp.id_asignatura and cm.id_malla = sp.id_malla
			CROSS APPLY OPENJSON(mpd.raes_json) as j
			where mcp.estado = '1'
				AND mpd.estado = '3' 
				AND mpd.estado_curso = '8'
				AND mpp.estado = '3'
				AND mpd.cierre_manual in ('0','2')
				AND mpd.raes_json IS NOT NULL
				AND JSON_VALUE(mpd.raes_json, '$."' + j.[key] + '".estado') COLLATE SQL_Latin1_General_CP1_CI_AS = '5'
						--AND mpd.id IN  ('37', '39', '43', '51', '52')
		"""
		return pd.read_sql(query, con=self.conn)
	
	def getProcesoDiarioEtapa1(self):
		query= '''
    		SELECT 
    		    mcp.id
    		    ,mcp.id_programa
    		    ,mcp.id_seccion
    		    ,(CASE WHEN mcp.clave_curso = '' THEN  
					(SELECT 
						 left(cv.codigo,3)
						FROM cvprograma as cv
						where cv.schedule_idprogram = mcp.id_programa
						and cv.schedule_idseccion = mcp.id_seccion) 
				ELSE  mcp.clave_curso
				END ) as tipo_proceso
    		    ,(CASE WHEN mcp.id_course = '' THEN  
					(SELECT 
						 SUBSTRING(cv.codigo, CHARINDEX('-', cv.codigo) + 1, LEN(cv.codigo)) 
						FROM cvprograma as cv
						where cv.schedule_idprogram = mcp.id_programa
						and cv.schedule_idseccion = mcp.id_seccion) 
				ELSE  mcp.id_course
				END ) as id_proceso
    		    ,mcp.id_asignatura
    		    ,mcp.horas_malla
    		    ,(SELECT 
    		        top 1 us.[data]
    		    FROM user_detail as us
    		    where us.user_id = mtp.id_teacher
    		    and us.fieldid = 4289) as tarifa
    		    ,[fecha_inicio_horario]
    		    ,[fecha_fin_horario]
    		    ,(SELECT 
    		        top 1 us.[data]
    		    FROM user_detail as us
    		    where us.user_id = mtp.id_teacher
    		    and us.fieldid = 423) as codigo_teacher
    		    ,(SELECT 
    		        CONCAT(FORMAT(DATEADD(MONTH, 1, scsh.[fecha_inicio]), 'MM'), '-', FORMAT(DATEADD(MONTH, 1, scsh.[fecha_inicio]), 'yyyy')) as periodo,
    		        (sum(DATEDIFF(minute,scsh.[fecha_inicio],scsh.[fecha_final]))*1.0/60.0 +
    		            (SELECT sum(convert(decimal(10,4),scc.outsesion))*90.0/60.0
    		            FROM schedule_cal_course_history as scc
    		            WHERE scc.id_programa = scsh.id_programa
    		            and scc.id_seccion = scsh.id_seccion
    		            and scc.estado = '1'
    		            and scc.id_course = scsh.id_course)) as horas
    		    FROM schedule_cal_sesion_history as scsh 
    		    join schedule_program as sp on sp.id_program = scsh.id_programa and sp.estado = '1'
    		    join schedule_seccion as sc on sc.id_seccion = scsh.id_seccion and sc.id_programa = sp.id_program
    		    join malla_academica as ma on ma.id = sp.id_malla and ma.grado = 5
    		    join cvprograma as cv on cv.schedule_idprogram = sp.id_program and cv.schedule_idseccion = sc.id_seccion
    		    where scsh.estado = '1'
    		    AND sp.id_program = mcp.id_programa
    		    and sc.id_seccion = mcp.id_seccion
    		    and scsh.id_course = mcp.id_asignatura
    		    group by scsh.id_programa, scsh.id_seccion, scsh.id_course, CONCAT(FORMAT(DATEADD(MONTH, 1, scsh.[fecha_inicio]), 'MM'), '-', FORMAT(DATEADD(MONTH, 1, scsh.[fecha_inicio]), 'yyyy'))
    		    FOR JSON PATH) as detalle
    		    ,mpd.id as id_detalle
    		FROM manage_pago_curso_programa as mcp 
    		join manage_pago_curso_teacher_programa as mtp on mtp.id_programa_curso = mcp.id
    		JOIN manage_pago_curso_proceso_detalle as mpd ON mpd.id_teacher_programa = mtp.id 
    		    AND mpd.estado = '3' 
    		    AND mpd.estado_curso = '1'  -- Listos para procesar 1 por procesar 3 errores y que lo vuelva a intentar
    		JOIN manage_pago_curso_proceso as mpp ON mpp.id = mpd.id_curso_proceso AND mpp.estado = '3'
    		where mcp.estado = '1';
    '''
		return pd.read_sql(query, con=self.conn)

	def getProcesoDiarioEtapa2(self):
		query= '''
			SELECT
			    mcp.id AS id_programa,
			    mpd.id as id_detalle
			FROM manage_pago_curso_programa AS mcp
			JOIN manage_pago_curso_teacher_programa AS mtp ON mtp.id_programa_curso = mcp.id
			JOIN manage_pago_curso_proceso_detalle AS mpd  ON mpd.id_teacher_programa = mtp.id
			JOIN manage_pago_curso_proceso AS mpp ON mpp.id = mpd.id_curso_proceso
			WHERE mcp.estado = '1'
			    AND mpd.estado = '3'
			    AND mpd.estado_curso = '4'
			    AND mpp.estado = '3';
    '''
		return pd.read_sql(query, con=self.conn)
	
	def getProcesoDiarioEtapa3(self):
		query= '''
			SELECT
			    mcp.id AS id_programa,
			    mpd.id as id_detalle
			FROM manage_pago_curso_programa AS mcp
			JOIN manage_pago_curso_teacher_programa AS mtp ON mtp.id_programa_curso = mcp.id
			JOIN manage_pago_curso_proceso_detalle AS mpd  ON mpd.id_teacher_programa = mtp.id
			JOIN manage_pago_curso_proceso AS mpp ON mpp.id = mpd.id_curso_proceso
			WHERE mcp.estado = '1'
			    AND mpd.estado = '3'
			    AND mpd.estado_curso = '6'
			    AND mpp.estado = '3';
    '''
		return pd.read_sql(query, con=self.conn)

	def actualizar_estado_curso(self, id_detalle, nuevo_estado, mensaje_validaciones=None):
		cursor = self.conn.cursor()
		if mensaje_validaciones:
			query ="""
			UPDATE manage_pago_curso_proceso_detalle
			SET estado_curso = ?, mensaje_validaciones = ?
			WHERE id = ?
			"""
			cursor.execute(query,(nuevo_estado, mensaje_validaciones, id_detalle))
		else:
			query = """
			UPDATE manage_pago_curso_proceso_detalle 
			SET estado_curso = ?
			WHERE id = ?
			"""
			cursor.execute(query, (nuevo_estado, id_detalle))
		self.conn.commit()
		cursor.close()


	def actualizar_estado_curso_lote(self, lista_id_detalles, nuevo_estado, mensaje_validaciones=None):
		if not lista_id_detalles:
			print("[WARN] No hay registros para actualizar")
			return
		cursor = self.conn.cursor()
		placeholders = ','.join(['?' for _ in lista_id_detalles])
		if mensaje_validaciones:
			query = f"""
				UPDATE manage_pago_curso_proceso_detalle
				SET estado_curso = ?, mensaje_validaciones = ?
				WHERE id IN ({placeholders})
			"""
			# Los parámetros van: estado, mensaje, luego todos los IDs
			params = [nuevo_estado, mensaje_validaciones] + lista_id_detalles
			cursor.execute(query, params)
		else:
			query = f"""
			UPDATE manage_pago_curso_proceso_detalle
			SET estado_curso = ?
			WHERE id IN ({placeholders})
			"""
			# Los parámetros van: estado, luego todos los IDs
			params = [nuevo_estado] + lista_id_detalles
			cursor.execute(query, params)
		self.conn.commit()
		registros_actualizados = cursor.rowcount
		cursor.close()
		
		print(f"[DB] Actualizados {registros_actualizados} registros a estado {nuevo_estado}")
		return registros_actualizados

	def getCursosInicio(self):
		query = '''SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
					EXEC rpa_sistema_evaluacion_nogrado'''
		return pd.read_sql(query, con=self.conn)

	

	def registrarCursoRpaLog(self, curso_row, estado, error, mensaje_error=None):

		if mensaje_error is None:
			mensaje_error = ""

		get_val = curso_row.__getitem__ if hasattr(curso_row, "__getitem__") else lambda k: None

		try:
			id_program   = int(get_val('id_program'))
			id_seccion   = int(get_val('id_seccion'))
			id_calendar  = int(get_val('id_calendar'))
			id_course    = str(get_val('id_course')).strip()
			clave_curso  = str(get_val('CLAVECURSO')).strip()
			clave_programa = str(
				get_val('codigo_cv')
				if 'codigo_cv' in curso_row
				else get_val('CLAVEPROGRAMA')
			).strip()

			# Normalizamos los flags a 0 / 1
			estado_flag = 1 if estado else 0
			error_flag  = 1 if error else 0

			self.conn.autocommit = False
			query = """
				INSERT INTO cv_course_rpa_log (
					id_program,
					id_seccion,
					id_calendar,
					id_course,
					clavecurso,
					claveprograma,
					estado,
					fecha_ejecucion,
					error,
					mensaje_error
				)
				VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, ?)
			"""

			crsr = self.conn.cursor()
			crsr.execute(
				query,
				(
					id_program,
					id_seccion,
					id_calendar,
					id_course,
					clave_curso,
					clave_programa,
					estado_flag,
					error_flag,
					mensaje_error,
				)
			)
			self.conn.commit()

			print(
				"[RPA][LOG] Registrado en cv_course_rpa_log => "
				"id_program={}, id_seccion={}, id_calendar={}, id_course={}, clavecurso={}, estado={}, error={} , mensaje_error={}".format(
					id_program, id_seccion, id_calendar, id_course, clave_curso, estado_flag, error_flag, mensaje_error
				)
			)

		except Exception as e:
			print("[RPA][ERROR] Al registrarCursoRpaLog:", e)


	def registrarNotaPromedioRpaLog(self, codigo_programa, conf_notapromedio, mensaje=""):
		"""
		Actualiza en manage_certificados_nogrado por codigo_programa:
		conf_notapromedio: '0' no procesado | '1' ok | '2' con errores
		conf_notapromedio_message: detalle
		conf_notapromedio_fecha: fecha de ejecución
		"""
		if mensaje is None:
			mensaje = ""

		codigo_programa = str(codigo_programa).strip()
		conf_notapromedio = str(conf_notapromedio).strip()  # debe ser '0','1','2'

		if conf_notapromedio not in ("0", "1", "2"):
			raise ValueError(f"conf_notapromedio inválido: {conf_notapromedio} (usa '0','1','2')")

		prev_autocommit = getattr(self.conn, "autocommit", True)

		try:
			self.conn.autocommit = False

			query = """
				UPDATE manage_certificados_nogrado
				SET conf_notapromedio = ?,
					conf_notapromedio_message = ?,
					conf_notapromedio_fecha = GETDATE()
				WHERE codigo_programa = ?
			"""

			crsr = self.conn.cursor()
			crsr.execute(query, (conf_notapromedio, mensaje, codigo_programa))

			if crsr.rowcount == 0:
				# No encontró fila con ese codigo_programa
				self.conn.rollback()
				print(f"[RPA][WARN] No existe registro en manage_certificados_nogrado para codigo_programa={codigo_programa}")
				return False

			self.conn.commit()
			print(f"[RPA][LOG] NotaPromedio actualizado => codigo_programa={codigo_programa}, conf_notapromedio={conf_notapromedio}")
			return True

		except Exception as e:
			try:
				self.conn.rollback()
			except Exception:
				pass
			print("[RPA][ERROR] Al registrarNotaPromedioRpaLog:", e)
			return False

		finally:
			try:
				self.conn.autocommit = prev_autocommit
			except Exception:
				pass


	def registrarEstadoRpaLog(self, codigo_programa, id, conf_estadofinal, mensaje=""):
		"""
		Actualiza en manage_certificados_alumnos por (codigo_programa, id):
		conf_estadofinal: '0' no procesado | '1' ok | '2' con errores
		conf_estadofinal_message: detalle
		conf_estadofinal_fecha: fecha de ejecución
		"""
		if mensaje is None:
			mensaje = ""

		codigo_programa = str(codigo_programa).strip()
		id = str(id).strip()
		conf_estadofinal = str(conf_estadofinal).strip()  

		if conf_estadofinal not in ("0", "1", "2"):
			raise ValueError(f"conf_estadofinal inválido: {conf_estadofinal} (usa '0','1','2')")

		prev_autocommit = getattr(self.conn, "autocommit", True)

		try:
			self.conn.autocommit = False

			query = """
				UPDATE manage_certificados_alumnos
				SET conf_estadofinal = ?,
					conf_estadofinal_message = ?,
					conf_estadofinal_fecha = GETDATE()
				WHERE codigo_programa = ?
				AND id = ?
			"""

			crsr = self.conn.cursor()
			crsr.execute(query, (conf_estadofinal, mensaje, codigo_programa, id))

			if crsr.rowcount == 0:
				self.conn.rollback()
				print(f"[RPA][WARN] No existe registro en manage_certificados_alumnos para codigo_programa={codigo_programa}, id={id}")
				return False

			self.conn.commit()
			print(f"[RPA][LOG] EstadoFinal actualizado => codigo_programa={codigo_programa}, id={id}, conf_estadofinal={conf_estadofinal}")
			return True

		except Exception as e:
			try:
				self.conn.rollback()
			except Exception:
				pass
			print("[RPA][ERROR] Al registrarEstadoRpaLog:", e)
			return False

		finally:
			try:
				self.conn.autocommit = prev_autocommit
			except Exception:
				pass

	
	def registrarVistaPreviaCertificadoRpaLog(self, codigo_programa, identidad, conf_vistaprevia, mensaje=""):
		"""
		Actualiza en manage_certificados_alumnos por (codigo_programa, identidad):
		conf_vistaprevia: '0' no procesado | '1' ok | '2' con errores
		conf_vistaprevia_message: detalle
		conf_vistaprevia_fecha: fecha de ejecución (GETDATE)
		"""
		if mensaje is None:
			mensaje = ""

		codigo_programa = str(codigo_programa).strip()
		identidad = str(identidad).strip()
		conf_vistaprevia = str(conf_vistaprevia).strip()

		if conf_vistaprevia not in ("0", "1", "2"):
			raise ValueError(
				"conf_vistaprevia inválido: {} (usa '0','1','2')".format(conf_vistaprevia)
			)

		prev_autocommit = getattr(self.conn, "autocommit", True)

		try:
			self.conn.autocommit = False

			query = """
				UPDATE manage_certificados_alumnos
				SET conf_vistaprevia = ?,
					conf_vistaprevia_message = ?,
					conf_vistaprevia_fecha = GETDATE()
				WHERE codigo_programa = ?
				AND identidad = ?
			"""

			crsr = self.conn.cursor()
			crsr.execute(query, (conf_vistaprevia, mensaje, codigo_programa, identidad))

			if crsr.rowcount == 0:
				self.conn.rollback()
				print("[RPA][WARN] No existe registro en manage_certificados_alumnos para codigo_programa={}, identidad={}".format(
					codigo_programa, identidad
				))
				return False

			self.conn.commit()
			print("[RPA][LOG] VistaPrevia actualizada => codigo_programa={}, identidad={}, conf_vistaprevia={}".format(
				codigo_programa, identidad, conf_vistaprevia
			))
			return True

		except Exception as e:
			try:
				self.conn.rollback()
			except Exception:
				pass
			print("[RPA][ERROR] Al registrarVistaPreviaCertificado:", e)
			return False

		finally:
			try:
				self.conn.autocommit = prev_autocommit
			except Exception:
				pass


	def registrarCertificadosPublicadosRpaLog(self, codigo_programa, identidad, conf_emision, mensaje=""):
		"""
		Actualiza en manage_certificados_alumnos por (codigo_programa, identidad):
		conf_emision: '0' no procesado | '1' ok | '2' con errores
		conf_emision_message: detalle
		conf_emision_fecha: fecha de ejecución (GETDATE)
		"""
		if mensaje is None:
			mensaje = ""

		codigo_programa = str(codigo_programa).strip()
		identidad = str(identidad).strip()
		conf_emision = str(conf_emision).strip()

		if conf_emision not in ("0", "1", "2"):
			raise ValueError(
				"conf_emision inválido: {} (usa '0','1','2')".format(conf_emision)
			)

		prev_autocommit = getattr(self.conn, "autocommit", True)

		try:
			self.conn.autocommit = False

			query = """
				UPDATE manage_certificados_alumnos
				SET conf_emision = ?,
					conf_emision_message = ?,
					conf_emision_fecha = GETDATE()
				WHERE codigo_programa = ?
				AND identidad = ?
			"""

			crsr = self.conn.cursor()
			crsr.execute(query, (conf_emision, mensaje, codigo_programa, identidad))

			if crsr.rowcount == 0:
				self.conn.rollback()
				print("[RPA][WARN] No existe registro en manage_certificados_alumnos para codigo_programa={}, identidad={}".format(
					codigo_programa, identidad
				))
				return False

			self.conn.commit()
			print("[RPA][LOG] Emisión actualizada => codigo_programa={}, identidad={}, conf_emision={}".format(
				codigo_programa, identidad, conf_emision
			))
			return True

		except Exception as e:
			try:
				self.conn.rollback()
			except Exception:
				pass
			print("[RPA][ERROR] Al registrarCertificadosPublicadosRpaLog:", e)
			return False

		finally:
			try:
				self.conn.autocommit = prev_autocommit
			except Exception:
				pass

	
	def mostrarManageCertificadosAlumnos(self):
		"""
		Muestra por consola columnas clave de dbo.manage_certificados_alumnos.
		Convierte fechas a varchar para evitar problemas con datetimeoffset.
		"""

		query = """
			SELECT
				id,
				identidad,
				codigo_programa,
				CONVERT(varchar(33), fecha_apto_creacion, 127) AS fecha_apto_creacion,
				CONVERT(varchar(33), fecha_certificado_creacion, 127) AS fecha_certificado_creacion,
				conf_estadofinal,
				conf_estadofinal_message,
				CONVERT(varchar(33), conf_estadofinal_fecha, 127) AS conf_estadofinal_fecha
			FROM dbo.manage_certificados_alumnos
			ORDER BY conf_estadofinal_fecha DESC, id DESC;
		"""

		cursor = self.conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()

		colnames = [c[0] for c in cursor.description]

		print("\n[RPA] Registros en manage_certificados_alumnos (columnas clave):")

		if not rows:
			print("[RPA]   (sin registros)")
			return

		data_str = [["" if v is None else str(v) for v in row] for row in rows]

		widths = []
		for idx, col in enumerate(colnames):
			max_len = len(col)
			for r in data_str:
				if len(r[idx]) > max_len:
					max_len = len(r[idx])
			widths.append(max_len)

		row_fmt = " | ".join("{{:{}}}".format(w) for w in widths)
		sep = "-+-".join("-" * w for w in widths)

		print(sep)
		print(row_fmt.format(*colnames))
		print(sep)

		for r in data_str:
			print(row_fmt.format(*r))

		print(sep)


	def mostrarManageCertificadosAlumnosProcesoVisaPreviaCertificados(self):
		"""
		Muestra por consola columnas clave de dbo.manage_certificados_alumnos.
		Convierte fechas a varchar para evitar problemas con datetimeoffset.
		"""

		query = """
			SELECT
				id,
				identidad,
				codigo_programa,
				CONVERT(varchar(33), fecha_apto_creacion, 127) AS fecha_apto_creacion,
				CONVERT(varchar(33), fecha_certificado_creacion, 127) AS fecha_certificado_creacion,
				conf_estadofinal,
				conf_vistaprevia,
				conf_vistaprevia_message,
				CONVERT(varchar(33), conf_vistaprevia_fecha, 127) AS conf_vistaprevia_fecha
			FROM dbo.manage_certificados_alumnos
			ORDER BY conf_vistaprevia_fecha DESC, id DESC;
		"""

		cursor = self.conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()

		colnames = [c[0] for c in cursor.description]

		print("\n[RPA] Registros en manage_certificados_alumnos (columnas clave):")

		if not rows:
			print("[RPA]   (sin registros)")
			return

		data_str = [["" if v is None else str(v) for v in row] for row in rows]

		widths = []
		for idx, col in enumerate(colnames):
			max_len = len(col)
			for r in data_str:
				if len(r[idx]) > max_len:
					max_len = len(r[idx])
			widths.append(max_len)

		row_fmt = " | ".join("{{:{}}}".format(w) for w in widths)
		sep = "-+-".join("-" * w for w in widths)

		print(sep)
		print(row_fmt.format(*colnames))
		print(sep)

		for r in data_str:
			print(row_fmt.format(*r))

		print(sep)

	

	def mostrarManageCertificadosAlumnosProcesoPublicarCertificados(self):
		"""
		Muestra por consola columnas clave de dbo.manage_certificados_alumnos.
		Convierte fechas a varchar para evitar problemas con datetimeoffset.
		"""

		query = """
			SELECT
				id,
				identidad,
				codigo_programa,
				CONVERT(varchar(33), fecha_apto_creacion, 127) AS fecha_apto_creacion,
				CONVERT(varchar(33), fecha_certificado_creacion, 127) AS fecha_certificado_creacion,
				conf_estadofinal,
				conf_emision,
				conf_emision_message,
				CONVERT(varchar(33), conf_emision_fecha, 127) AS conf_vistaprevia_fecha
			FROM dbo.manage_certificados_alumnos
			ORDER BY conf_vistaprevia_fecha DESC, id DESC;
		"""

		cursor = self.conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()

		colnames = [c[0] for c in cursor.description]

		print("\n[RPA] Registros en manage_certificados_alumnos (columnas clave):")

		if not rows:
			print("[RPA]   (sin registros)")
			return

		data_str = [["" if v is None else str(v) for v in row] for row in rows]

		widths = []
		for idx, col in enumerate(colnames):
			max_len = len(col)
			for r in data_str:
				if len(r[idx]) > max_len:
					max_len = len(r[idx])
			widths.append(max_len)

		row_fmt = " | ".join("{{:{}}}".format(w) for w in widths)
		sep = "-+-".join("-" * w for w in widths)

		print(sep)
		print(row_fmt.format(*colnames))
		print(sep)

		for r in data_str:
			print(row_fmt.format(*r))

		print(sep)



	def resetEstadoFinalAlumno(self, codigo_programa=None, id=None):
		"""
		Resetea columnas de EstadoFinal en manage_certificados_alumnos con filtro:
		- Si pasas codigo_programa: resetea ese programa
		- Si pasas id: resetea ese alumno
		- Si pasas ambos: resetea el alumno en ese programa
		"""

		codigo_programa = ("" if codigo_programa is None else str(codigo_programa).strip())
		id = ("" if id is None else str(id).strip())

		if not codigo_programa and not id:
			raise ValueError("Debes enviar al menos codigo_programa o id para resetEstadoFinalAlumnosFiltro().")

		prev_autocommit = getattr(self.conn, "autocommit", True)

		try:
			self.conn.autocommit = False

			query = """
				UPDATE dbo.manage_certificados_alumnos
				SET conf_estadofinal = '0',
					conf_estadofinal_message = '',
					conf_estadofinal_fecha = NULL
				WHERE 1=1
			"""
			params = []

			if codigo_programa:
				query += " AND codigo_programa = ?"
				params.append(codigo_programa)

			if id:
				query += " AND id = ?"
				params.append(id)

			crsr = self.conn.cursor()
			crsr.execute(query, params)

			if crsr.rowcount == 0:
				self.conn.rollback()
				print("[RPA][WARN] No se encontraron registros para reset con esos filtros.")
				return False

			self.conn.commit()
			print(f"[RPA][LOG] Reset EstadoFinal (filtro) OK. Filas afectadas: {crsr.rowcount}")
			return True

		except Exception as e:
			try:
				self.conn.rollback()
			except Exception:
				pass
			print("[RPA][ERROR] Al resetEstadoFinalAlumnosFiltro:", e)
			return False

		finally:
			try:
				self.conn.autocommit = prev_autocommit
			except Exception:
				pass



	def getEstados(self):
		query = '''SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
					EXEC rpa_manage_confestadofinal_nogrado'''
		return pd.read_sql(query, con=self.conn)
	
	
	def getCertificadosVistaPrevia(self):
		query = '''SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
					EXEC rpa_manage_confvistaprevia_nogrado'''
		return pd.read_sql(query, con=self.conn)
	

	def getCertificadosPublicar(self):
		query = '''SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
					EXEC rpa_manage_emision_nogrado'''
		return pd.read_sql(query, con=self.conn)
	

	def getProgramasSinNotaPromedio(self):
		query = '''SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
					EXEC rpa_nota_promedio_programa'''
		return pd.read_sql(query, con=self.conn)



	def getRetirosProgramaEtapa(self, etapa=''):
		query = "EXEC rpa_retiro_programa_curso {etapa}".format(etapa=etapa)
		return pd.read_sql(query, con=self.conn)
    
	'''
	def getcursosByCodProgram(self, codigo_programa=''):
		query = "EXEC manage_get_cursos_byProgram '','{}'".format(codigo_programa)
		return pd.read_sql(query, con=self.conn)
	'''
	def getcursosByCodProgram(self, codigo_programa=''):
		query = """	SELECT [CLAVEPROGRAMA]
					,[CLAVECURSO]
					,[CODCURSO]
					,[NOMBRECURSO]
					,[estado]
					,[CLAVEASIGNATURA]
				FROM [cv_course]
				where CLAVEPROGRAMA = '{}'
				and estado = '1'
                """
		query = query.format(codigo_programa)
		return pd.read_sql(query, con=self.conn)
	
	def changeStateProcesoRetiro(self, etapa1='', valor_etapa=''):
        
		try:

			self.conn.autocommit = False
			query = """
				UPDATE manage_retiros_reincorp
                SET rpa_estado = '{valor_etapa}'
                WHERE id_solicitud = {id_solicitud}
                AND id_proceso = {id_proceso} 
            """
			query = query.format(valor_etapa=valor_etapa,id_solicitud=etapa1['id_solicitud'],id_proceso =etapa1['id_proceso'])
            #print(query)
			crsr = self.conn.cursor()
			crsr.execute(query)
			self.conn.commit()
			return True
		except Exception as e:
            #print(e)
			self.conn.rollback()
			return False
		
	def closeRPA(self, elemento=''):
        
		try:

			self.conn.autocommit = False
			crsr = self.conn.cursor()
			query = """
                SELECT
                   mri.id_solicitud
                FROM manage_retiros_reincorp_rpa as mri
                WHERE mri.cant_inlcluir > 0
	            and mri.estado = 0
                and mri.id_solicitud = {id_solicitud}
                and mri.id_proceso = {id_proceso}
            """
			query = query.format(id_solicitud=elemento['id_solicitud'],id_proceso=elemento['id_proceso'])
			information_df = pd.read_sql(query, con=self.conn)
			if information_df.empty == True:
				query = """
                    UPDATE manage_retiros_reincorp
                    SET soporte = '1'
                        ,usuario_sopote = 1
                        ,soporte_email = '1'
                        ,administracion = '1'
                        ,administracion_email = '1'
                        ,rpa_estado = '2'
                    WHERE id_solicitud = {id_solicitud}
                    and id_proceso = {id_proceso}
                    """
				query = query.format(id_solicitud=elemento['id_solicitud'],id_proceso=elemento['id_proceso'])
				crsr.execute(query)

				query = """
                    SELECT
                    top 1 ss.id_programa
                        ,ss.id_seccion
                        ,ss.cvprograma
                        ,ss.id_calendar 
                    FROM system_sync as ss
                    WHERE ss.cvprograma = '{programa}'
                    and ss.subtipo = 'synCampus'
                    and ss.tipo = 'calendar'
                    order by ss.id_calendar desc
                """
				query = query.format(programa=elemento['programa'])
				sync_df = pd.read_sql(query, con=self.conn)
				if sync_df.empty == True:
					query = """
                        INSERT INTO system_sync VALUES 
                        ({id_programa},{id_seccion},'{programa}',0,'calendar','synCampus',0,'0','{fecha}','{fecha}')
                    """
					query = query.format(id_programa=elemento['id_programa']
                                ,id_seccion=elemento['id_seccion']
                                ,programa=elemento['programa']
                                ,fecha=time.strftime('%Y-%m-%d %H:%M:%S'))
					crsr.execute(query)
				else:
					element_sync = sync_df.iloc[0]
					query = """
                        UPDATE system_sync
                        SET errors = 0
                          ,estado = '0'
                          ,fecha_modificacion = '{fecha}'
                        WHERE id_programa = {id_programa}
                        and id_seccion = {id_seccion}
                        and cvprograma = '{programa}'
                        and tipo = 'calendar'
                        and subtipo = 'synCampus'
                        and id_calendar = {id_calendar}
                    """
					query = query.format(id_programa=element_sync['id_programa']
                                ,id_seccion=element_sync['id_seccion']
                                ,programa=element_sync['cvprograma']
                                ,id_calendar=element_sync['id_calendar']
                                ,fecha=time.strftime('%Y-%m-%d %H:%M:%S'))
					crsr.execute(query)

                #aqui es para los retirar los cursos de canvas
				query = """
                    SELECT 
                        ss.id_programa
                        ,ss.id_seccion
                        ,ss.cvprograma
                    FROM system_sync as ss
                    WHERE ss.cvprograma = '{programa}'
                    and ss.subtipo = 'synCanvasCourse'
                    and ss.tipo = 'retiro'
                """
				query = query.format(programa=elemento['programa'])
				sync_df = pd.read_sql(query, con=self.conn)
				if sync_df.empty == True:
					query = """
                        INSERT INTO system_sync VALUES 
                        ({id_programa},{id_seccion},'{programa}',0,'retiro','synCanvasCourse',0,'0','{fecha}','{fecha}')
                    """
					query = query.format(id_programa=elemento['id_programa']
                                ,id_seccion=elemento['id_seccion']
                                ,programa=elemento['programa']
                                ,fecha=time.strftime('%Y-%m-%d %H:%M:%S'))
					crsr.execute(query)
				else:
					element_sync = sync_df.iloc[0]
					query = """
                        UPDATE system_sync
                        SET errors = 0
                          ,estado = '1'
                          ,fecha_modificacion = '{fecha}'
                        WHERE id_programa = {id_programa}
                        and id_seccion = {id_seccion}
                        and cvprograma = '{programa}'
                        and tipo = 'synCanvasCourse'
                        and subtipo = 'retiro'
                        and id_calendar = {id_calendar}
                    """
					query = query.format(id_programa=element_sync['id_programa']
                                ,id_seccion=element_sync['id_seccion']
                                ,programa=element_sync['cvprograma']
                                ,fecha=time.strftime('%Y-%m-%d %H:%M:%S'))
					crsr.execute(query)

				self.conn.commit()
				return 1
			else:	
				self.conn.commit()
				return 2
		except Exception as e:
			print(e)
			self.conn.rollback()
			return 3
	
	
	def getCertificadosInicio(self):
		query = """
			SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
			EXEC rpa_manage_certificados_nogrado
		"""
		return pd.read_sql(query, con=self.conn)
	
	def updateConfCertificado(self, codigo_programa, estado, mensaje_error=None):
		crsr = None
		try:
			estado = str(estado)
			if estado not in ("1", "2"):
				raise ValueError("Estado inválido")

			#Si es exitoso, el mensaje debe ser NULL
			if estado == "1":
				mensaje_error = None
			#else:
			#	mensaje_error = mensaje_error or ""

			query = """
				UPDATE manage_certificados_nogrado
				SET conf_certificado = ?,
					conf_certificado_message = ?,
					conf_certificado_fecha = GETDATE()
				WHERE codigo_programa = ?
			"""

			crsr = self.conn.cursor()
			crsr.execute(query, (estado, mensaje_error, codigo_programa))
			self.conn.commit()

			print(f"[RPA] conf_certificado={estado} actualizado para {codigo_programa}")
			return True

		except Exception as e:
			self.conn.rollback()
			print(f"[RPA][ERROR] updateConfCertificado: {e}")
			return False

		finally:
			if crsr:
				crsr.close()
	
	def getformatosCertificadosPendientes(self):
		query = """
			SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
			EXEC rpa_manage_formatocertificados_nogrado
		"""
		return pd.read_sql(query, con=self.conn)
	
	def updateForCertificado(self, codigo_programa, estado, mensaje_error=None):
		crsr = None
		try:
			estado = str(estado)
			if estado not in ("1", "2"):
				raise ValueError("Estado inválido")

			#Si es exitoso
			if estado == "1":
				mensaje_error = None

			query = """
				UPDATE dbo.manage_certificados_nogrado
				SET for_certificado = ?,
					for_certificado_message = ?,
					for_certificado_fecha = GETDATE()
				WHERE codigo_programa = ?
			"""

			crsr = self.conn.cursor()
			crsr.execute(query, (estado, mensaje_error, codigo_programa))
			self.conn.commit()

			print(f"[RPA] for_certificado={estado} actualizado para {codigo_programa}")
			return True

		except Exception as e:
			self.conn.rollback()
			print(f"[RPA][ERROR] updateForCertificado: {e}")
			return False

		finally:
			if crsr:
				crsr.close()

	def getPagosProfesores(self):
		query = """
			SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
			EXEC rpa_manage_pago_profesores_process
		"""
		cur = self.conn.cursor()
		cur.execute(query)

		# Resultset 1: PROGRAMAS
		cols1 = [c[0] for c in cur.description]
		rows1 = cur.fetchall()
		df_programas = pd.DataFrame.from_records(rows1, columns=cols1)

		# Resultset 2: DETALLE CURSOS
		df_detalle = pd.DataFrame()
		if cur.nextset() and cur.description:
			cols2 = [c[0] for c in cur.description]
			rows2 = cur.fetchall()
			df_detalle = pd.DataFrame.from_records(rows2, columns=cols2)

		cur.close()
		return df_programas, df_detalle
	
	def updateDocentesDetalle(self, codigo_detalle, estado_curso, mensaje=None):
		crsr = None
		try:
			estado_curso = str(estado_curso)
			if estado_curso not in ("0", "1", "2"):
				raise ValueError("Estado inválido (use 0/1/2)")

			# Si es OK, limpiamos mensaje
			if estado_curso == "1":
				mensaje = None

			query = """
				UPDATE manage_pago_curso_proceso_detalle
				SET estado_curso = ?,
					mensaje_validaciones = ?,
					fecha_creacion_curso = GETDATE()
				WHERE id = ?;
			"""

			crsr = self.conn.cursor()
			crsr.execute(query, (estado_curso, mensaje, int(codigo_detalle)))
			self.conn.commit()

			print(f"[RPA] estado_curso={estado_curso} actualizado para codigo_detalle={codigo_detalle}")
			return True

		except Exception as e:
			try:
				self.conn.rollback()
			except Exception:
				pass
			print(f"[RPA][ERROR] updateDocentesDetalle: {e}")
			return False

		finally:
			if crsr:
				crsr.close()
	
	def updateDocentesPadre(self, codigo_padre):
		crsr = None
		try:
			# Si existe algún curso != 1 , queda pendiente (estado_rpa = 1)
			query_pendientes = """
				SELECT COUNT(1)
				FROM manage_pago_curso_proceso_detalle
				WHERE id_curso_proceso = ?
				AND ISNULL(estado_curso,'0') <> '1';
			"""

			query_ok = """
				UPDATE manage_pago_curso_proceso
				SET estado_rpa = '2',
					fecha_proceso = GETDATE()
				WHERE id = ?;
			"""

			query_pend = """
				UPDATE manage_pago_curso_proceso
				SET estado_rpa = '1'
				WHERE id = ?;
			"""

			crsr = self.conn.cursor()
			crsr.execute(query_pendientes, (int(codigo_padre),))
			pendientes = crsr.fetchone()[0]

			if pendientes == 0:
				crsr.execute(query_ok, (int(codigo_padre),))
				print(f"[RPA] Padre {codigo_padre} -> estado_rpa=2 (todo OK)")
			else:
				crsr.execute(query_pend, (int(codigo_padre),))
				print(f"[RPA] Padre {codigo_padre} -> estado_rpa=1 (pendientes: {pendientes})")

			self.conn.commit()
			return True

		except Exception as e:
			try:
				self.conn.rollback()
			except Exception:
				pass
			print(f"[RPA][ERROR] updateDocentesPadre: {e}")
			return False

		finally:
			if crsr:
				crsr.close()
	
	def getCursosSistemaEvaluacion(self):
		query = """
				SELECT 
				pnc_alert_course_scores.id,
				pnc_alert_course_scores.program_id,
				pnc_alert_course_scores.course_id,
				pnc_alert_course_scores.teacher_id,
				pnc_alert_course_scores.calendar_id,
				pnc_alert_course_scores.seccion_id,
				pnc_alert_course_scores.program_type_id,
				pnc_alert_course_scores.grade_id,

				CONVERT(VARCHAR, pnc_alert_course_scores.date_last_session, 120) as date_last_session,
				CONVERT(VARCHAR, pnc_alert_course_scores.date_last_verification, 120) as date_last_verification,
				CONVERT(VARCHAR, pnc_alert_course_scores.created_at, 120) as created_at,
				CONVERT(VARCHAR, pnc_alert_course_scores.updated_at, 120) as updated_at,
				CONVERT(VARCHAR, pnc_alert_course_scores.registration_date, 120) as registration_date,
				CONVERT(VARCHAR, pnc_alert_course_scores.date_found_score, 120) as date_found_score,

				pnc_alert_course_scores.sum_scores,
				pnc_alert_course_scores.exception_by_program_type,
				pnc_alert_course_scores.exception_by_program,
				pnc_alert_course_scores.exception_by_course,
				pnc_alert_course_scores.exception_by_course_program,
				pnc_alert_course_scores.score_registered,
				pnc_alert_course_scores.qty_days_deadline,
				pnc_alert_course_scores.audit_log,

				u.email,
				ud.data as cod_teacher,
				CONCAT(u.apellido_paterno, ' ', u.apellido_materno, ', ', u.nombres) as full_name, 
				cm.cod_curso,
				sp.id_program,
				sp.nombre_programa as program_name, 
				CAST(cm.nombre as nvarchar(max)) as course_name,
				sc.nombre_seccion as seccion_name, 
				ma.grado as type_grade, 
				scal.nombre as cycle_name,
				cv.codigo,
				cvc.CODCURSO,
				cvc.CLAVECURSO,
				cvc.NOMBRECICLO,

				
				CONVERT(VARCHAR,
					DATEADD(
						DAY,
						ISNULL(pnc_alert_course_scores.qty_days_deadline,0) + 1,
						pnc_alert_course_scores.date_last_session
					),120
				) as fecha_limite

			FROM pnc_alert_course_scores

			INNER JOIN users as u 
				ON pnc_alert_course_scores.teacher_id = u.id 

			JOIN user_detail as ud 
				ON u.id = ud.user_id 

			JOIN schedule_program as sp 
				ON pnc_alert_course_scores.program_id = sp.id_program 

			JOIN schedule_seccion as sc 
				ON pnc_alert_course_scores.seccion_id = sc.id_seccion 

			JOIN malla_academica as ma 
				ON sp.id_malla = ma.id 
				AND ma.grado = 1

			JOIN curso_malla as cm 
				ON cm.id_malla = ma.id 
				AND cm.cod_curso = pnc_alert_course_scores.course_id

			JOIN schedule_calendar as scal 
				ON pnc_alert_course_scores.calendar_id = scal.id_calendar

			JOIN cvprograma as cv 
				ON cv.schedule_idprogram = sp.id_program 
				AND cv.schedule_idseccion = sc.id_seccion

			JOIN cv_course as cvc 
				ON LTRIM(cvc.CODCURSO) = LTRIM(cm.cod_curso) 
				AND cvc.CLAVEPROGRAMA = cv.codigo 
				AND cvc.estado = '1'

			WHERE score_registered = '0' 
			AND grade_id = 1
			AND ma.no_notificar_docentes = '0'
			AND ud.fieldid = 423
			AND exception_by_program_type = '0'
			AND exception_by_program = '0'
			AND exception_by_course = '0'
			AND exception_by_course_program = '0'

			
			AND CONVERT(DATETIME,
				DATEADD(
					DAY,
					ISNULL(pnc_alert_course_scores.qty_days_deadline,0) + 1,
					pnc_alert_course_scores.date_last_session
				)
			) BETWEEN DATEADD(DAY,-10,GETDATE()) AND DATEADD(DAY,10,GETDATE())

			AND (
				SELECT COUNT(1)
				FROM STRING_SPLIT(cv.codigo, '-')
			) > 2  

			ORDER BY fecha_limite ASC
		"""

		return pd.read_sql(query, con=self.conn)
	

	def updateCertificadoToAptos(self):
		crsr = None
		try:
			query = """
					update manage_certificados_alumnos
					set certificado = '1'
					where id in (
						SELECT 
						mca.id
						FROM cohort as co
						join cvprograma as cv on cv.codigo = co.programa
						join schedule_program as sp on sp.id_program = cv.schedule_idprogram
						join schedule_seccion as sc on sc.id_seccion = cv.schedule_idseccion and sc.id_programa = sp.id_program
						join malla_academica as ma on ma.id = sp.id_malla
						join system_data as sd on sd.id = ma.tipo_programa
						JOIN manage_certificados_alumnos mca 
							ON co.IDENTIDAD = mca.identidad 
							AND co.programa = mca.codigo_programa
							and mca.certificado = 0
							and mca.conf_estadofinal = '0'
						join manage_certificados_nogrado as mcn
							on mcn.codigo_programa = co.programa
							and mcn.conf_notapromedio = '1'
							and mcn.conf_certificado = '1'
							and mcn.for_certificado = '1'
						WHERE co.estado = '1'
						and ISNULL(mca.apto, 0) = 1)
			"""

			crsr = self.conn.cursor()
			crsr.execute(query)
			self.conn.commit()
			return True

		except Exception as e:
			self.conn.rollback()
			print(f"[RPA][ERROR] updateForCertificado: {e}")
			return False

		finally:
			if crsr:
				crsr.close()
	
	
	def registrarCambioFechasRpaLog(self, codigo_programa,conf_cambiofecha, mensaje=""):
		"""
		Actualiza en manage_certificados_nogrado por (codigo_programa, identidad):
		conf_cambiofecha: '0' pendiente | '1' exitoso/aprobado | '2' solicitud de cambio enviada
		conf_cambiofecha_message: detalle
		conf_cambiofecha_fecha: fecha de ejecucion (GETDATE)
		"""
		if mensaje is None:
			mensaje = ""

		codigo_programa = str(codigo_programa).strip()
		conf_cambiofecha = str(conf_cambiofecha).strip()

		if conf_cambiofecha not in ("0", "1", "2"):
			raise ValueError(
				"conf_cambiofecha invalido: {} (usa '0','1','2')".format(conf_cambiofecha)
			)

		prev_autocommit = getattr(self.conn, "autocommit", True)

		try:
			self.conn.autocommit = False

			query = """
				UPDATE manage_certificados_nogrado
				SET conf_cambiofecha = ?,
					conf_cambiofecha_message = ?,
					conf_cambiofecha_fecha = GETDATE()
				WHERE codigo_programa = ?
			"""

			crsr = self.conn.cursor()
			crsr.execute(query, (conf_cambiofecha, mensaje, codigo_programa))

			if crsr.rowcount == 0:
				self.conn.rollback()
				print("[RPA][WARN] No existe registro en manage_certificados_nogrado para codigo_programa={}".format(
					codigo_programa
				))
				return False

			self.conn.commit()
			print("[RPA][LOG] CambioFechas actualizado => codigo_programa={}, conf_cambiofecha={}".format(
				codigo_programa, conf_cambiofecha
			))
			return True

		except Exception as e:
			try:
				self.conn.rollback()
			except Exception:
				pass
			print("[RPA][ERROR] Al registrarCambioFechasRpaLog:", e)
			return False

		finally:
			try:
				self.conn.autocommit = prev_autocommit
			except Exception:
				pass

	
	def getValidacionDuplicados(self):
		query = """
				SELECT 
			cp.id_programa
			,isnull(caddd.valor,0) as id_proceso
			,cd.valor as fecha_inauguracion
			,dateadd(day,1, CASE 
				WHEN TRY_CONVERT(DATE, CAST(cd.valor AS NVARCHAR(50)), 23) >= '1753-01-01'
				THEN CAST(
						TRY_CONVERT(DATE, CAST(cd.valor AS NVARCHAR(50)), 23)
						AS DATETIME)
				ELSE NULL
			END ) as fecha
			,cpdd.valor as fecha_cierre_matricula
			,cpddd.valor as nombre_proceso
			FROM current_programa as cp
			join current_programa_detalle as cd on cd.id_programa = cp.id_programa 
				and cd.id_campo = 1061
				and cd.business = '0'
			join current_programa_detalle as cpdd on cpdd.id_programa = cp.id_programa 
				and cpdd.id_campo = 1432
				and cpdd.business = '0'
			join current_programa_detalle as cpddd on cpddd.id_programa = cp.id_programa 
				and cpddd.id_campo = 4506
				and cpddd.business = '0'
			left join current_programa_detalle as caddd on caddd.id_programa = cp.id_programa 
				and caddd.id_campo = 4645
				and caddd.business = '0'
			where cp.estado = 1170
			and (SELECT 
				 COUNT(1)
				FROM current_programa_detalle as cpd
				where cpd.id_programa = cp.id_programa 
				and cpd.id_campo = 3672
				and TRY_CAST(cpd.valor as bigint) = 3676
				and cpd.business = '0') = 0 
			and GETDATE() between dateadd(day,1, CASE 
				WHEN TRY_CONVERT(DATE, CAST(cd.valor AS NVARCHAR(50)), 23) >= '1753-01-01'
				THEN CAST(
						TRY_CONVERT(DATE, CAST(cd.valor AS NVARCHAR(50)), 23)
						AS DATETIME)
				ELSE NULL
			END ) and dateadd(day,1, CASE 
				WHEN TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23) >= '1753-01-01'
				THEN CAST(
						TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23)
						AS DATETIME)
				ELSE NULL
			END )
			
		"""

		return pd.read_sql(query, con=self.conn)
	
	def insertCodigoProcesoCurrentPlan(self, row, codigo_proceso):
		crsr = None
		try:
			self.conn.autocommit = False
			crsr = self.conn.cursor()
			query = """
						INSERT INTO current_programa_detalle VALUES 
						({id_programa},{id_campo},NULL,'{codigo_proceso}',0,1,'{fecha}')
				"""
			query = query.format(id_programa=row['id_programa']
													,id_campo=4645
													,codigo_proceso=codigo_proceso
													,fecha=time.strftime('%Y-%m-%d %H:%M:%S'))
			crsr.execute(query)

			self.conn.commit()
			return True

		except Exception as e:
			self.conn.rollback()
			print(f"[RPA][ERROR] updateForCertificado: {e}")
			return False

		finally:
			if crsr:
				crsr.close()


	def getValidacionAnos(self):
		query = """
				SELECT 
			cp.id_programa
			,isnull(caddd.valor,0) as id_proceso
			,dateadd(day,-4, CASE 
				WHEN TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23) >= '1753-01-01'
				THEN CAST(
						TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23)
						AS DATETIME)
				ELSE NULL
			END ) as fecha_cierre_matricula
			,cpdd.valor as fecha_cierre_matricula
			,cpdd.valor as fecha_cierre_matricula
			,(SELECT 
				 datepart(yy,MIN(scsh.fecha_inicio))
				FROM schedule_program as sp
				join schedule_calendar as sc on sc.id_programa = sp.id_program 
						and sc.id_estado = '202'
				join schedule_cal_sesion_history as scsh on scsh.id_calendar = sc.id_calendar
				where sp.current_id_programa = cp.id_programa
				and scsh.estado = '1'
          	) as anho_inicio
			,cpddd.valor as nombre_proceso
			FROM current_programa as cp
			join current_programa_detalle as cpddd on cpddd.id_programa = cp.id_programa 
				and cpddd.id_campo = 4506
				and cpddd.business = '0'
			join current_programa_detalle as cpdd on cpdd.id_programa = cp.id_programa 
				and cpdd.id_campo = 1432
				and cpdd.business = '0'
			join current_programa_detalle as caddd on caddd.id_programa = cp.id_programa 
				and caddd.id_campo = 4645
				and caddd.business = '0'
			where cp.estado = 1170
			and (SELECT 
				 COUNT(1)
				FROM current_programa_detalle as cpd
				where cpd.id_programa = cp.id_programa 
				and cpd.id_campo = 3672
				and TRY_CAST(cpd.valor as bigint) = 3676
				and cpd.business = '0') = 0
			and GETDATE() between Dateadd(day,-4, CASE 
				WHEN TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23) >= '1753-01-01'
				THEN CAST(
						TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23)
						AS DATETIME)
				ELSE NULL
			END ) and dateadd(day,1, CASE 
				WHEN TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23) >= '1753-01-01'
				THEN CAST(
						TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23)
						AS DATETIME)
				ELSE NULL
			END )
			and isnull(caddd.valor,0) != 0
			and case when (SELECT 
							COUNT(distinct ss.id_seccion)
						FROM schedule_program as sp
				
						join schedule_seccion as sc on sc.id_programa = sp.id_program
							and sc.estado = '1'
						join schedule_calendar as ss on ss.id_programa = sp.id_program
							and ss.id_seccion = sc.id_seccion 
						where sp.current_id_programa = cp.id_programa
						and sp.estado = '1'
						and ss.id_estado = '202') = 0 then '0'
					else 
						case when (SELECT 
							COUNT(distinct ss.id_seccion)
						FROM schedule_program as sp
				
						join schedule_seccion as sc on sc.id_programa = sp.id_program
							and sc.estado = '1'
						join schedule_calendar as ss on ss.id_programa = sp.id_program
							and ss.id_seccion = sc.id_seccion 
						where sp.current_id_programa = cp.id_programa
						and sp.estado = '1'
						and ss.id_estado = '202') = (SELECT 
				    COUNT(distinct ss.id_seccion)
				FROM schedule_program as sp
				
				join schedule_seccion as sc on sc.id_programa = sp.id_program
					and sc.estado = '1'
				join schedule_calendar as ss on ss.id_programa = sp.id_program
					and ss.id_seccion = sc.id_seccion 
				where sp.current_id_programa = cp.id_programa
				and sp.estado = '1'
				and ss.id_estado = '202') then '1' else '0' end
					end = '1'

		"""

		return pd.read_sql(query, con=self.conn)
	
	def getGeneracionCodigos(self):
		query = """
			SELECT 
			cp.id_programa
			,isnull(caddd.valor,0) as id_proceso
			,dateadd(day,-4, CASE 
				WHEN TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23) >= '1753-01-01'
				THEN CAST(
						TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23)
						AS DATETIME)
				ELSE NULL
			END ) as fecha_cierre_matricula
			,cpdd.valor as fecha_cierre_matricula
			,cpddd.valor as nombre_proceso
			FROM current_programa as cp
			
			join current_programa_detalle as cpddd on cpddd.id_programa = cp.id_programa 
				and cpddd.id_campo = 4506
				and cpddd.business = '0'
			join current_programa_detalle as cpdd on cpdd.id_programa = cp.id_programa 
				and cpdd.id_campo = 1432
				and cpdd.business = '0'
			join current_programa_detalle as cud on cud.id_programa = cp.id_programa 
				and cud.id_campo = 4648
				and cud.business = '0'
				and cud.valor = '1'
			join current_programa_detalle as caddd on caddd.id_programa = cp.id_programa 
				and caddd.id_campo = 4645
				and caddd.business = '0'
			where cp.estado = 1170
			and (SELECT 
				 COUNT(1)
				FROM current_programa_detalle as cpd
				where cpd.id_programa = cp.id_programa 
				and cpd.id_campo = 3672
				and TRY_CAST(cpd.valor as bigint) = 3676
				and cpd.business = '0') = 0 
			and (SELECT 
				 COUNT(1)
				FROM current_programa_detalle as cpd
				where cpd.id_programa = cp.id_programa 
				and cpd.id_campo = 4649
				and cpd.valor = '1'
				and cpd.business = '0') = 0 
			and GETDATE() >= Dateadd(day,-1, CASE 
				WHEN TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23) >= '1753-01-01'
				THEN CAST(
						TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23)
						AS DATETIME)
				ELSE NULL
			END )
			and isnull(caddd.valor,0) != 0

		"""

		return pd.read_sql(query, con=self.conn)
	
	def getEmptyCiclo(self):
		query = """
			SELECT
				cp.id_programa
				,(SELECT
								top 1 cpd.valor
								from current_programa_detalle as cpd
								where cpd.id_programa = cp.id_programa
								and cpd.id_campo = (
																		SELECT  sd.id
																		FROM system_data as sd
																		where sd.idnumber_data = 'ccp_nompro'
																		and sd.field_idnumber = 66)
								and cpd.business = '0'
								and cpd.valor != '')  as nombre_comercial
				,(SELECT
								top 1 cpd.valor
								from current_programa_detalle as cpd
								where cpd.id_programa = cp.id_programa
								and cpd.id_campo = (
																		SELECT  sd.id
																		FROM system_data as sd
																		where sd.idnumber_data = 'ccp_nombre_academico'
																		and sd.field_idnumber = 66)
								and cpd.business = '0'
								and cpd.valor != '')  as nombre_academico
				,(SELECT
								top 1 convert(varchar, convert(datetime,cpd.valor,21),103)
								from current_programa_detalle as cpd
								where cpd.id_programa = cp.id_programa
								and cpd.id_campo = (
																		SELECT  sd.id
																		FROM system_data as sd
																		where sd.idnumber_data = 'ccp_inicio_clases'
																		and sd.field_idnumber = 66)
								and cpd.business = '0'
								and cpd.valor != '') as inicio_clases
				,(SELECT
						top 1 cpd.valor
						from current_programa_detalle as cpd
						where cpd.id_programa = cp.id_programa
						and cpd.id_campo = (
																SELECT  sd.id
																FROM system_data as sd
																where sd.idnumber_data = 'ccp_correlativo'
																and sd.field_idnumber = 66)
						and cpd.business = '0'
						and cpd.valor != '') as correlativo
				,isnull((SELECT
						top 1 cpd.valor
						from current_programa_detalle as cpd
						where cpd.id_programa = cp.id_programa
						and cpd.id_campo = (
																SELECT  sd.id
																FROM system_data as sd
																where sd.idnumber_data = 'ccp_calendario_cv'
																and sd.field_idnumber = 66)
						and cpd.business = '0'
						and cpd.valor != ''),'') as calendario
				
			FROM current_programa as cp
			where
					
					(SELECT
							COUNT(1)
							from current_programa_detalle as cpd
							where cpd.id_programa = cp.id_programa
							and cpd.id_campo = (
																	SELECT  sd.id
																	FROM system_data as sd
																	where sd.idnumber_data = 'ccp_nompro'
																	and sd.field_idnumber = 66)
							and cpd.business = '0'
							and cpd.valor != '') > 0
					and
					(SELECT
							COUNT(1)
							from current_programa_detalle as cpd
							where cpd.id_programa = cp.id_programa
							and cpd.id_campo = (
																	SELECT  sd.id
																	FROM system_data as sd
																	where sd.idnumber_data = 'ccp_nombre_academico'
																	and sd.field_idnumber = 66)
							and cpd.business = '0'
							and cpd.valor != '') > 0
					and
					(SELECT
							COUNT(1)
							from current_programa_detalle as cpd
							where cpd.id_programa = cp.id_programa
							and cpd.id_campo = (
																	SELECT  sd.id
																	FROM system_data as sd
																	where sd.idnumber_data = 'ccp_inicio_clases'
																	and sd.field_idnumber = 66)
							and cpd.business = '0'
							and cpd.valor != '') > 0
					and
					(SELECT
							COUNT(1)
							from current_programa_detalle as cpd
							where cpd.id_programa = cp.id_programa
							and cpd.id_campo = (
																	SELECT  sd.id
																	FROM system_data as sd
																	where sd.idnumber_data = 'ccp_correlativo'
																	and sd.field_idnumber = 66)
							and cpd.business = '0'
							and cpd.valor != '') > 0
					and
					(SELECT
							COUNT(1)
							from current_programa_detalle as cpd
							where cpd.id_programa = cp.id_programa
							and cpd.id_campo = (
																	SELECT  sd.id
																	FROM system_data as sd
																	where sd.idnumber_data = 'ccp_calendario_cv'
																	and sd.field_idnumber = 66)
							and cpd.business = '0'
							and cpd.valor != '') > 0
					and
					(SELECT
							COUNT(1)
							from current_programa_detalle as cpd
							where cpd.id_programa = cp.id_programa
							and cpd.id_campo = (
																	SELECT  sd.id
																	FROM system_data as sd
																	where sd.idnumber_data = 'ccp_codigociclo_cv'
																	and sd.field_idnumber = 66)
							and cpd.business = '0'
							and cpd.valor != '') = 0
					and
					(SELECT
							COUNT(1)
							from current_programa_detalle as cpd
							where cpd.id_programa = cp.id_programa
							and cpd.id_campo = (
																	SELECT  sd.id
																	FROM system_data as sd
																	where sd.idnumber_data = 'ccp_propuesta_academica'
																	and sd.field_idnumber = 66)
							and cpd.business = '0'
							and cpd.valor != '') > 0
					and
					(SELECT
						COUNT(1)
						FROM schedule_program as sp
						JOIN cvprograma as cv on cv.schedule_idprogram = sp.id_program
						WHERE sp.estado = '1'
						AND sp.current_id_programa = cp.id_programa) = 0
					and
					(SELECT
							top 1 cpd.valor
							from current_programa_detalle as cpd
							where cpd.id_programa = cp.id_programa
							and cpd.id_campo = (
																	SELECT  sd.id
																	FROM system_data as sd
																	where sd.idnumber_data = 'ccp_correlativo'
																	and sd.field_idnumber = 66)
							and cpd.business = '0') != '1'
					and
					(SELECT
							COUNT(1)
							from current_programa_detalle as cpd
							where cpd.id_programa = cp.id_programa
							and cpd.id_campo = (
																	SELECT  sd.id
																	FROM system_data as sd
																	where sd.idnumber_data = 'ccp_addciclocero'
																	and sd.field_idnumber = 66)
							and cpd.business = '0'
							and (cpd.valor != '' and cpd.valor!='0')) > 0
		"""

		return pd.read_sql(query, con=self.conn)
	
	def getNombreCiclo(self, nombre_ciclo):
		query = """
				
			SELECT TOP 1
				STUFF(
					NOMBRECICLO,
					LEN(LEFT(NOMBRECICLO, CHARINDEX(' - ', NOMBRECICLO) - 1))
						- CHARINDEX(' ', REVERSE(LEFT(NOMBRECICLO, CHARINDEX(' - ', NOMBRECICLO) - 1))) + 2,
					CHARINDEX(' - ', NOMBRECICLO)
						- (
							LEN(LEFT(NOMBRECICLO, CHARINDEX(' - ', NOMBRECICLO) - 1))
							- CHARINDEX(' ', REVERSE(LEFT(NOMBRECICLO, CHARINDEX(' - ', NOMBRECICLO) - 1))) + 2
						),
					'XXXX'
				) AS NuevoNombreCiclo
			FROM cv_course
			WHERE CLAVEPROGRAMA in (
				SELECT
				top 1 codigo
				from cvprograma 
				where codigo like '%-{nombre_ciclo}'
				order by fecha_creacion desc

			)
			ORDER BY FECHAINICIO ASC;


		"""

		query = query.format(nombre_ciclo=nombre_ciclo)

		return pd.read_sql(query, con=self.conn)
	
	def registerDataToCurrent(self, id_programa, promocion_romanos,nombre_ciclo, ciclo_pucp, codigo_ciclo ):
		crsr = None
		try:
			self.conn.autocommit = False
			crsr = self.conn.cursor()
			

			query = """
						INSERT INTO current_programa_detalle VALUES 
						({id_programa},{id_campo},NULL,'{valor}',0,1,'{fecha}')
				"""
			query = query.format(id_programa=id_programa
									,id_campo=3463
									,valor=promocion_romanos
									,fecha=time.strftime('%Y-%m-%d %H:%M:%S'))
			crsr.execute(query)

			query = """
						INSERT INTO current_programa_detalle VALUES 
						({id_programa},{id_campo},NULL,'{valor}',0,1,'{fecha}')
				"""
			query = query.format(id_programa=id_programa
									,id_campo=3464
									,valor=nombre_ciclo
									,fecha=time.strftime('%Y-%m-%d %H:%M:%S'))
			crsr.execute(query)
			
			
			query = """
						INSERT INTO current_programa_detalle VALUES 
						({id_programa},{id_campo},NULL,'{valor}',0,1,'{fecha}')
				"""
			query = query.format(id_programa=id_programa
									,id_campo=4651
									,valor=ciclo_pucp
									,fecha=time.strftime('%Y-%m-%d %H:%M:%S'))
			crsr.execute(query)


			query = """
						INSERT INTO current_programa_detalle VALUES 
						({id_programa},{id_campo},NULL,'{valor}',0,1,'{fecha}')
				"""
			query = query.format(id_programa=id_programa
									,id_campo=3465
									,valor=codigo_ciclo
									,fecha=time.strftime('%Y-%m-%d %H:%M:%S'))
			crsr.execute(query)
			
			
			self.conn.commit()
			return True

		except Exception as e:
			self.conn.rollback()
			print(f"[RPA][ERROR] updateForCertificado: {e}")
			return False

		finally:
			if crsr:
				crsr.close()


	def registerItemDataToCurrent(self, id_programa, id_campo, value):
		crsr = None
		try:
			self.conn.autocommit = False
			crsr = self.conn.cursor()
			

			query = """
						UPDATE current_programa_detalle
						SET
							valor = ?,
							fecha_creacion = ?
						WHERE id_programa = ?
						AND id_campo = ?
						AND business = '0';

						IF @@ROWCOUNT = 0
						BEGIN
							INSERT INTO current_programa_detalle
							VALUES
							(
								?, ?, NULL, ?, 0, 1, ?
							);
						END
				"""
			fecha=time.strftime('%Y-%m-%d %H:%M:%S')
			crsr.execute(
				query,
				(
					value, fecha, id_programa, id_campo,
					id_programa, id_campo, value, fecha
				)
			)

			self.conn.commit()
			return True

		except Exception as e:
			self.conn.rollback()
			print(f"[RPA][ERROR] updateForCertificado: {e}")
			return False

		finally:
			if crsr:
				crsr.close()



	def getCRMPrograms(self):
		query = """
				SELECT 
			cp.id_programa
			,isnull(caddd.valor,0) as id_proceso
			,cpdd.valor as fecha_cierre_matricula
			,cpddd.valor as nombre_proceso
			,isnull((SELECT 
				  top 1 cupd.valor
				FROM current_programa_detalle as cupd
				where cupd.id_programa = cp.id_programa
				and cupd.business = '0'
				and cupd.id_campo = 1057
				),'') as nombre_marketing
			,isnull((SELECT 
				  top 1 cupd.valor
				FROM current_programa_detalle as cupd
				where cupd.id_programa = cp.id_programa
				and cupd.business = '0'
				and cupd.id_campo = 1083
				),'') as nombre_cisam
			,(SELECT 
				  top 1 cupd.valor
				FROM current_programa_detalle as cupd
				where cupd.id_programa = cp.id_programa
				and cupd.business = '0'
				and cupd.id_campo = 3466
				) as codigo_crm
			FROM current_programa as cp
			
			join current_programa_detalle as cpddd on cpddd.id_programa = cp.id_programa 
				and cpddd.id_campo = 4506
				and cpddd.business = '0'
			join current_programa_detalle as cpdd on cpdd.id_programa = cp.id_programa 
				and cpdd.id_campo = 1432
				and cpdd.business = '0'
			join current_programa_detalle as cud on cud.id_programa = cp.id_programa 
				and cud.id_campo = 4648
				and cud.business = '0'
				and cud.valor = '1'
			join current_programa_detalle as caddd on caddd.id_programa = cp.id_programa 
				and caddd.id_campo = 4645
				and caddd.business = '0'
			where cp.estado = 1170
			and (SELECT 
				 COUNT(1)
				FROM current_programa_detalle as cpd
				where cpd.id_programa = cp.id_programa 
				and cpd.id_campo = 3672
				and TRY_CAST(cpd.valor as bigint) = 3676
				and cpd.business = '0') = 0 
			and (SELECT 
				 COUNT(1)
				FROM current_programa_detalle as cpd
				where cpd.id_programa = cp.id_programa 
				and cpd.id_campo = 4649
				and cpd.valor = '1'
				and cpd.business = '0') = 0 
			and (SELECT 
				 COUNT(1)
				FROM current_programa_detalle as cpd
				where cpd.id_programa = cp.id_programa 
				and cpd.id_campo = 4650
				and cpd.valor = '1'
				and cpd.business = '0') = 0
			and GETDATE() >= Dateadd(day,+1, CASE 
				WHEN TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23) >= '1753-01-01'
				THEN CAST(
						TRY_CONVERT(DATE, CAST(cpdd.valor AS NVARCHAR(50)), 23)
						AS DATETIME)
				ELSE NULL
			END )
			and isnull(caddd.valor,0) != 0
			and isnull((SELECT 
				  top 1 case when LEN(cupd.valor) > 3 then '1' else '0'  end
				FROM current_programa_detalle as cupd
				where cupd.id_programa = cp.id_programa
				and cupd.business = '0'
				and cupd.id_campo = 3466
				),'0') = '1'


		"""

		return pd.read_sql(query, con=self.conn)