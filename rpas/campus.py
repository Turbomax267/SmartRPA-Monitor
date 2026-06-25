import sys
import time
import pandas as pd
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from resultado_rpa import ResultadoRPA

from datetime import datetime, date
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException

import smtplib
import unicodedata
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
import os
import re
import glob
import shutil
from storage_backends import MediaStorage
from cambiar_fechas import main as ejecutar_cambio_fechas_main

config = configparser.ConfigParser()
config.read('/var/www/my_config_rpa.cnf')
SCREENSHOT_PATH = "/var/www/centrumonline.pucp.edu.pe/rpa_campusvirtual/abel/screenshots" 

sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')

class CampusConnect():
	def __init__(self, **kwargs):
		self.username = config['rravelo']['user']
		self.password = config['rravelo']['password']
		self.user_pago = config['pagos']['user']
		self.pass_pago = config['pagos']['password']
		self.email =  config['emailrpase']['email']
		self.emails_pago =  config['emailpago']['email']
		self.emails_cert =  config['emailcert']['email']
		self.smpt_user = config['smpt']['user']
		self.smpt_pass = config['smpt']['pass']
		self.bcc =  config['emailrpase']['bcc']
		self.url_pandora = config['url']['pandora']
		self.url_eros = config['url']['eros']
		self.url_ares = config['url']['ares']
		self.cer_primero = config['certificado']['primer']
		self.cer_segundo = config['certificado']['segundo']
		self.user_pago_alb = config['alberto']['user']
		self.pass_pago_alb = config['alberto']['password']
		self.emailvalideval =  config['emailvalideval']['email']
		self.usereval = config['vpucutay']['user']
		self.passeval = config['vpucutay']['password']
		self.email_portal_asistencia = config['portalasistencia']['email']
		self.password_portal_asistencia = config['portalasistencia']['password']
		self.emailvaldupli = config['emailvaldupli']['email']
		self.emailvalanho = config['emailvalanho']['email']
		self.emailgencodigo = config['emailgencodigo']['email']
		self.emaildnicrm = config['emaildnicrm']['email']
		
	
	def getDriver(self, download_path=None):
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--headless') # ensure GUI is off
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--disable-dev-shm-usage')
		chrome_options.add_argument("--lang=es-PE")
		# Configurar carpeta de descarga
		if download_path:
			prefs = {
				"download.default_directory"         : download_path,
				"download.prompt_for_download"       : False,
				"download.directory_upgrade"         : True,
				"safebrowsing.enabled"               : True,
				"plugins.always_open_pdf_externally" : True
			}
			chrome_options.add_experimental_option("prefs", prefs)
		chromedriver_autoinstaller.install()
		driver = webdriver.Chrome(options=chrome_options)
		# Habilitar descargas en modo headless
		if download_path:
			driver.execute_cdp_cmd(
				"Page.setDownloadBehavior",
				{
					"behavior"     : "allow",
					"downloadPath" : download_path
				}
			)
		return driver


	def logInCampusVirtualSistemaEval(self, driver=''):
		driver.get(f"{self.url_pandora}/pucp/login")
		wait = WebDriverWait(driver, 10)

		usuario = self.usereval
		password = self.passeval
		
		username_input =  WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
		)
		username_input.send_keys(usuario)
		password_input =  WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
		)
		password_input.send_keys(password)
		submit_login_button = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@class='submit izq']"))
		)
		
		submit_login_button.click()

		try:
			wait.until(
				lambda d:
					d.find_elements(By.XPATH, "//div[contains(@class,'cierre-correcto')]") 
			)
		except TimeoutException:
			#emails = 'abarbozab@pucp.pe'
			#Colocar correo de manuel tambien
			emails = [self.email]
			cc = [] 
			bcc = [self.bcc]

			subject = 'FALLO VALIDACIÓN INICIO DE SESIÓN RPA SISTEMA DE EVALUACIÓN NO GRADO'
			from_address = "Plataforma-Centrum <noreply@centrummailing.pucp.edu.pe>"

			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)       

			if cc:
				msg['Cc'] = ", ".join(cc)      

			msg['Subject'] = subject
			text_email_student = f"""
							<html>
							<body>
								<p>Estimados,</p>
								<p>El RPA de creación de sistema de evaluación no pudo iniciar sesión en el Campus Virtual.</p>
							</body>
							</html>
							"""     
			msg.attach(MIMEText(text_email_student, 'html'))

			msg_string = msg.as_string()

			toaddrs = emails + cc + bcc         

			
			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			server.sendmail(from_address, toaddrs, msg_string)
			server.quit()
			print("No se pudo validar el login: no se encontró ni 'cierre-correcto', "
				"ni 'tabParticipando', ni el formulario de login.")
			'''
			raise RuntimeError(
				"No se pudo validar el login: no se encontró ni 'cierre-correcto', "
				"ni 'tabParticipando', ni el formulario de login."
			)
			'''

		if driver.find_elements(By.XPATH, "//div[contains(@class,'cierre-correcto')]"):
			print("[RPA] Login correcto (pantalla 'Inicio de sesión correcto').")
			return driver

		print("Estado de login indeterminado tras enviar el formulario.")
		#raise RuntimeError("Estado de login indeterminado tras enviar el formulario.")

	def logInCampusVirtual(self, driver=''):
		driver.get(f"{self.url_pandora}/pucp/login")
		wait = WebDriverWait(driver, 10)

		usuario = self.username
		password = self.password
		
		username_input =  WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
		)
		username_input.send_keys(usuario)
		password_input =  WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
		)
		password_input.send_keys(password)
		submit_login_button = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@class='submit izq']"))
		)
		
		submit_login_button.click()

		try:
			wait.until(
				lambda d:
					d.find_elements(By.XPATH, "//div[contains(@class,'cierre-correcto')]") 
			)
		except TimeoutException:
			#emails = 'abarbozab@pucp.pe'
			#Colocar correo de manuel tambien
			emails = [self.email]
			cc = [] 
			bcc = [self.bcc]

			subject = 'FALLO VALIDACIÓN INICIO DE SESIÓN RPA SISTEMA DE EVALUACIÓN NO GRADO FUNCION GENERAL'
			from_address = "Plataforma-Centrum <noreply@centrummailing.pucp.edu.pe>"

			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)       

			if cc:
				msg['Cc'] = ", ".join(cc)      

			msg['Subject'] = subject
			text_email_student = f"""
							<html>
							<body>
								<p>Estimados,</p>
								<p>El RPA de creación de sistema de evaluación no pudo iniciar sesión en el Campus Virtual.</p>
							</body>
							</html>
							"""     
			msg.attach(MIMEText(text_email_student, 'html'))

			msg_string = msg.as_string()

			toaddrs = emails + cc + bcc         

			
			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			server.sendmail(from_address, toaddrs, msg_string)
			server.quit()
			print("No se pudo validar el login: no se encontró ni 'cierre-correcto', "
				"ni 'tabParticipando', ni el formulario de login.")
			'''
			raise RuntimeError(
				"No se pudo validar el login: no se encontró ni 'cierre-correcto', "
				"ni 'tabParticipando', ni el formulario de login."
			)
			'''

		if driver.find_elements(By.XPATH, "//div[contains(@class,'cierre-correcto')]"):
			print("[RPA] Login correcto (pantalla 'Inicio de sesión correcto').")
			return driver

		print("Estado de login indeterminado tras enviar el formulario.")
		#raise RuntimeError("Estado de login indeterminado tras enviar el formulario.")
		
	def realizarRetiroCampusVirtual(self, url_get='', driver='', codigo=''):
		driver.get(f"{self.url_eros}/pucp/")
		time.sleep(5)
		driver.get(url_get)
		time.sleep(5)
		driver.get(f"{self.url_eros}/pucp/")
		time.sleep(5)
		driver.get(url_get)
		time.sleep(5)

		wait = WebDriverWait(driver, 10)
		
		tipoingreso = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@name='tipoingresobusca']")))
		select_tipo_ingreso = Select(tipoingreso)
		select_tipo_ingreso.select_by_visible_text('MATRICULADO')
		search = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='pucpRayaLink']")))
		search.click()

		table = wait.until(EC.presence_of_element_located((By.XPATH,  "//table[@id='tInscripciones']")))
		rows = table.find_elements(By.TAG_NAME,'tr')

		#obtenemos el elemento con el código que estamos buscando
		row_element = 0
		for i in range(len(rows)):
			if len(rows[i].find_elements(By.NAME,'codigo'))>0:
				if codigo == rows[i].find_elements(By.NAME,'codigo')[0].get_attribute('value'):
					row_element = i
		
		print(rows[row_element].text)
		tipo_ingreso = rows[row_element].find_elements(By.NAME,'tipoingreso')
		select_tipo_ingreso = Select(tipo_ingreso[0])
		print(len(select_tipo_ingreso.options))
		select_tipo_ingreso.select_by_visible_text('RETIRADO')
		
		table_opciones = wait.until(EC.presence_of_element_located((By.XPATH,  "//table[@class='pucpTablaTitulo']")))
		buttons = table_opciones.find_elements(By.TAG_NAME,'button')

		button_element = 0
		for i in range(len(buttons)):
			if(buttons[i].text=='Grabar'):
				button_element = i
		print(buttons[button_element].text)
		buttons[button_element].click()
		time.sleep(3)
		alter_obj = driver.switch_to.alert
		print(alter_obj.text)
		alter_obj.accept()
		time.sleep(3)

	def realizarIncorpoCampusVirtual(self, url_get='', driver='', codigo=''):
		driver.get(f"{self.url_eros}/pucp/")
		time.sleep(5)
		driver.get(url_get)
		time.sleep(5)
		driver.get(f"{self.url_eros}/pucp/")
		time.sleep(5)
		driver.get(url_get)
		time.sleep(5)

		wait = WebDriverWait(driver, 10)
		
		tipoingreso = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@name='tipoingresobusca']")))
		select_tipo_ingreso = Select(tipoingreso)
		select_tipo_ingreso.select_by_visible_text('RETIRADO')
		search = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='pucpRayaLink']")))
		search.click()

		table = wait.until(EC.presence_of_element_located((By.XPATH,  "//table[@id='tInscripciones']")))
		rows = table.find_elements(By.TAG_NAME,'tr')

		#obtenemos el elemento con el código que estamos buscando
		row_element = 0
		for i in range(len(rows)):
			if len(rows[i].find_elements(By.NAME,'codigo'))>0:
				if codigo == rows[i].find_elements(By.NAME,'codigo')[0].get_attribute('value'):
					row_element = i
		
		print(rows[row_element].text)
		tipo_ingreso = rows[row_element].find_elements(By.NAME,'tipoingreso')
		select_tipo_ingreso = Select(tipo_ingreso[0])
		print(len(select_tipo_ingreso.options))
		select_tipo_ingreso.select_by_visible_text('MATRICULADO')
		
		table_opciones = wait.until(EC.presence_of_element_located((By.XPATH,  "//table[@class='pucpTablaTitulo']")))
		buttons = table_opciones.find_elements(By.TAG_NAME,'button')

		button_element = 0
		for i in range(len(buttons)):
			if(buttons[i].text=='Grabar'):
				button_element = i
		print(buttons[button_element].text)
		buttons[button_element].click()
		time.sleep(3)
		alter_obj = driver.switch_to.alert
		print(alter_obj.text)
		alter_obj.accept()
		time.sleep(3)
	
	def crearSistemaEvaluacionCampusVirtual(self, url_get='', driver=''):

		driver.get(url_get)
		time.sleep(5)

		wait = WebDriverWait(driver, 10)

		resultado = ResultadoRPA()

		try:
			print("[RPA] Buscando botón 'Crear sistema de evaluación'...")

			boton_crear = wait.until(
				EC.element_to_be_clickable((
					By.XPATH,
					"//button[contains(@onclick,'crearCalifica') "
					"and contains(@class,'pucpBoton')]"
				))
			)

			inputs = driver.find_elements(
				By.XPATH,
				"("
				"//input[(@type='radio' or @type='text' or @type='number' or @type='checkbox') "
				"       and not(contains(@style,'display:none'))]"
				" | //select[not(contains(@style,'display:none'))]"
				")"
			)


			if len(inputs) > 0:
				msg = ("Este es un curso que no se debería procesar")
				print("[RPA]", msg)
				resultado.estado = 1
				resultado.error = 0
				resultado.mensaje_error = msg
				resultado.continua = False
				return resultado

			print("[RPA] No hay sistema de evaluación. Creando...")
			boton_crear.click()
			time.sleep(2)

			link_forma = wait.until(
				EC.element_to_be_clickable((By.LINK_TEXT, "Forma de calificación"))
			)
			link_forma.click()
			print("[RPA] Botón crear encontrado, entrando a 'Forma de calificación'.")
			resultado.mensaje_error = "Sistema creado y se ingresó a Forma de calificación."
			resultado.continua = True

			return resultado

		except TimeoutException:
			print("[RPA] No se encontró botón 'Crear'. "
              "Validando estado de 'Forma de calificación'...")

			try:
				link_forma = wait.until(
					EC.element_to_be_clickable((By.LINK_TEXT, "Forma de calificación"))
				)
				link_forma.click()
				print("[RPA] Enlace 'Forma de calificación' encontrado y clickeado.")
			
				res_existe = self.existeSistemaEvaluacion(driver, wait)
				return res_existe

			except TimeoutException:
				msg = ("No hay enlace 'Forma de calificación")
				print("[RPA]", msg)
				resultado.estado = 0
				resultado.error = 0
				resultado.mensaje_error = msg
				resultado.continua = False
				return resultado
			
		except Exception as e:
			msg = "Error al validar existencia de sistema de evaluación: {}".format(e)
			print("[RPA][ERROR]", msg)
			resultado.estado = 0
			resultado.error = 1
			resultado.mensaje_error = msg
			resultado.continua = False
			return resultado
			
	def existeSistemaEvaluacion(self, driver, wait):

		resultado = ResultadoRPA()

		try:
			celda_formula = wait.until(
				EC.presence_of_element_located((
					By.XPATH,
					"//td[@class='pucpCelda']"
				))
			)
		except TimeoutException:
			msg = ("NO hay sistema configurado.")
			print("[RPA]", msg)
			resultado.continua = True
			return resultado

		except Exception as e:
			msg = "Error al verificar existencia de sistema de evaluación: {}".format(e)
			print("[RPA][ERROR]", msg)
			resultado.estado = 0
			resultado.error = 1
			resultado.mensaje_error = msg
			resultado.continua = False
			return resultado

		texto = (celda_formula.text or "").strip()

		if texto:
			print("[RPA] Fórmula del promedio final encontrada")
			resultado.estado = 1
			resultado.error = 0
			resultado.continua = False
			resultado.mensaje_error = (
				"Ya existe sistema de evaluación configurado".format(texto)
			)
		else:
			print("[RPA] La celda de fórmula está vacía. NO hay sistema de evaluación configurado.")
			resultado.continua = True
			

		return resultado
		
	def configurarFormaCalificacion(self, driver, tipo_evaluacion=0, identificador_curso_programa=''):

		wait = WebDriverWait(driver, 10)
		resultado = ResultadoRPA()

		try:

			boton_editar = wait.until(
				EC.element_to_be_clickable((
					By.XPATH,
					"//button[contains(@onclick,'editarFormula') and contains(@class,'pucpBoton')]"
				))
			)
			boton_editar.click()
			time.sleep(2)


			if identificador_curso_programa == 'codigo_cv':
				self.configurarFormaCalificacionPrograma(driver, wait)
			else:
				self.configurarFormaCalificacionCurso(driver, wait, tipo_evaluacion)
			
			radio_redondeado = driver.find_element(
				By.XPATH,
				"//form[@name='edicionFormula']//input[@type='radio'][1]"
			)
			radio_redondeado.click()

			campo_dec_formula = driver.find_element(
				By.XPATH,
				"//form[@name='edicionFormula']//input[@name='numDecimales']"
			)
			campo_dec_formula.clear()
			campo_dec_formula.send_keys("2")

			campo_maximo = driver.find_element(
				By.XPATH,
				"//form[@name='edicionFormula']//input[@name='maximoPuntaje']"
			)
			campo_maximo.clear()
			campo_maximo.send_keys("20")

			campo_min_aprob = driver.find_element(
				By.XPATH,
				"//form[@name='edicionFormula']//input[@name='puntajeMinAprob']"
			)
			campo_min_aprob.clear()
			campo_min_aprob.send_keys("10.51")

			boton_grabar_formula = driver.find_element(
				By.XPATH,
				"//form[@name='edicionFormula']//button[contains(@onclick,'guardarFormula')]"
			)
			boton_grabar_formula.click()
			time.sleep(2)

			print("[RPA] Sistema de evaluación configurado correctamente.")
			resultado.estado = 1
			resultado.error = 0
			resultado.continua = True
			resultado.mensaje_error = "Configuración de forma de calificación OK."

		except Exception as e:
			print("[RPA][ERROR] Al configurar forma de calificación:", e)
			resultado.estado = 0
			resultado.error = 1
			resultado.continua = False
			resultado.mensaje_error = "Error en configurarFormaCalificacion: {}".format(e)

		return resultado
	
	def configurarFormaCalificacionCurso(self, driver, wait, tipo_evaluacion=0):

		try:
			if tipo_evaluacion == 1:

				boton_anadir = wait.until(
					EC.element_to_be_clickable((
						By.XPATH,
						"//button[contains(@onclick,'anadirEvaluacion') "
						"and contains(@class,'pucpBoton')]"
					))
				)
				boton_anadir.click()
				time.sleep(1)

				tipo_eval = wait.until(
					EC.element_to_be_clickable((By.NAME, "tipoEvaluacion"))
				)
				select_tipo = Select(tipo_eval)
				select_tipo.select_by_value("00000026")

				campo_num_eval = driver.find_element(By.NAME, "numEvaluaciones")
				campo_num_eval.clear()
				campo_num_eval.send_keys("1")

				campo_decimales = driver.find_element(By.NAME, "numDecimales")
				campo_decimales.clear()
				campo_decimales.send_keys("2")

				campo_peso = driver.find_element(By.NAME, "peso")
				campo_peso.clear()
				campo_peso.send_keys("100")

				boton_grabar_eval = driver.find_element(
					By.XPATH,
					"//button[contains(@onclick,'grabarEvaluacion') "
					"and contains(@class,'pucpBoton')]"
				)
				boton_grabar_eval.click()
				time.sleep(2)

			else:
				evaluaciones = [
					("00000044", "40"),
					("00000034", "30"),
					("00000033", "30"),
				]

				for value_tipo, peso in evaluaciones:

					boton_anadir = wait.until(
						EC.element_to_be_clickable((
							By.XPATH,
							"//button[contains(@onclick,'anadirEvaluacion') "
							"and contains(@class,'pucpBoton')]"
						))
					)
					boton_anadir.click()
					time.sleep(1)

					tipo_eval = wait.until(
						EC.element_to_be_clickable((By.NAME, "tipoEvaluacion"))
					)
					select_tipo = Select(tipo_eval)
					select_tipo.select_by_value(value_tipo)

					campo_num_eval = driver.find_element(By.NAME, "numEvaluaciones")
					campo_num_eval.clear()
					campo_num_eval.send_keys("1")

					campo_decimales = driver.find_element(By.NAME, "numDecimales")
					campo_decimales.clear()
					campo_decimales.send_keys("2")

					campo_peso = driver.find_element(By.NAME, "peso")
					campo_peso.clear()
					campo_peso.send_keys(peso)

					boton_grabar_eval = driver.find_element(
						By.XPATH,
						"//button[contains(@onclick,'grabarEvaluacion') "
						"and contains(@class,'pucpBoton')]"
					)
					boton_grabar_eval.click()
					time.sleep(2)

		except Exception as e:
			raise

	def configurarFormaCalificacionPrograma(self, driver, wait):
		
		boton_anadir = wait.until(
			EC.element_to_be_clickable((
				By.XPATH,
				"//button[contains(@onclick,'anadirEvaluacion') and contains(@class,'pucpBoton')]"
			))
		)
		boton_anadir.click()
		time.sleep(1)

		tipo_eval = wait.until(EC.element_to_be_clickable((By.NAME, "tipoEvaluacion")))
		Select(tipo_eval).select_by_value("00000035")
		time.sleep(1) 

		wait.until(EC.visibility_of_any_elements_located((By.NAME, "arrCurso")))
		selects_curso = [
			s for s in driver.find_elements(By.NAME, "arrCurso")
			if s.is_displayed() and s.is_enabled()
		]

		for i in range(len(selects_curso)):
			try:
				sel = selects_curso[i]
				driver.execute_script("arguments[0].scrollIntoView({block:'center'});", sel)
				s = Select(sel)
				if len(s.options) > 1:
					idx = min(i + 1, len(s.options) - 1)
					s.select_by_index(idx)
			except StaleElementReferenceException:
				selects_curso = [
					s for s in driver.find_elements(By.NAME, "arrCurso")
					if s.is_displayed() and s.is_enabled()
				]
				sel = selects_curso[i]
				s = Select(sel)
				idx = min(i + 1, len(s.options) - 1)
				s.select_by_index(idx)

		
		campo_decimales = wait.until(
			EC.element_to_be_clickable((
				By.XPATH,
				"//form[@name='edicionEvaluacion']//input[@name='numDecimales']"
			))
		)
		campo_decimales.click()
		campo_decimales.send_keys(Keys.CONTROL, "a")
		campo_decimales.send_keys("2")

		campo_peso = wait.until(
			EC.element_to_be_clickable((
				By.XPATH,
				"//form[@name='edicionEvaluacion']//input[@name='peso']"
			))
		)
		campo_peso.click()
		campo_peso.send_keys(Keys.CONTROL, "a")
		campo_peso.send_keys("100")

		boton_grabar_eval = wait.until(
			EC.element_to_be_clickable((
				By.XPATH,
				"//form[@name='edicionEvaluacion']//button[contains(@onclick,'grabarEvaluacion') and contains(@class,'pucpBoton')]"
			))
		)
		boton_grabar_eval.click()
		time.sleep(2)

	def asignarEstadoFinal(self, url_get='', driver='', codigo='', estado_final=''):

		def _norm(txt):
			txt = (txt or "").strip().upper()
			txt = unicodedata.normalize("NFD", txt)
			txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")  
			txt = " ".join(txt.split())
			return txt

		def _select_estado(sel_obj, estado_objetivo):
			"""
			Selecciona por texto visible. Si no calza exacto (tildes/espacios),
			busca opción por comparación normalizada.
			"""
			try:
				sel_obj.select_by_visible_text(estado_objetivo)
				return True
			except Exception:
				obj_norm = _norm(estado_objetivo)
				for opt in sel_obj.options:
					if _norm(opt.text) == obj_norm:
						sel_obj.select_by_visible_text(opt.text)
						return True
			return False

		wait = WebDriverWait(driver, 10)
		resultado = ResultadoRPA()

		codigo = str(codigo).strip()
		estado_final = str(estado_final).strip()

		if not codigo or not estado_final:
			msg = "Parámetros inválidos: codigo/estado_final vacíos."
			print("[RPA][ERROR]", msg)
			resultado.estado = 2
			resultado.mensaje_error = msg
			resultado.continua = False
			return resultado

		try:
			driver.get(self.url_eros)
			time.sleep(2)
			driver.get(url_get)
			time.sleep(3)

			print("[RPA] URL:", driver.current_url)

			boton_editar = wait.until(
				EC.element_to_be_clickable((
					By.XPATH,
					"//button[contains(@onclick,'editar') and contains(@class,'pucpBoton')]"
				))
			)
			boton_editar.click()
			time.sleep(1)

			xpath_fila = "//table//tbody//tr[normalize-space(td[1])='{0}' or normalize-space(td[1]//a)='{0}']".format(codigo)
			fila = wait.until(EC.presence_of_element_located((By.XPATH, xpath_fila)))


			select_el = None
			try:
				select_el = fila.find_element(
					By.XPATH, ".//select[@name='estadoParticipante' and contains(@id,'cmbEst')]"
				)
			except Exception:
				select_el = None

			estado_actual_raw = ""
			if select_el is not None:
				sel = Select(select_el)
				estado_actual_raw = (sel.first_selected_option.text or "").strip()
			else:
				try:
					estado_actual_raw = (fila.find_element(By.XPATH, "./td[6]").text or "").strip()
				except Exception:
					estado_actual_raw = (fila.text or "").strip()

			estado_actual = _norm(estado_actual_raw)
			estado_objetivo = _norm(estado_final)


	
			permitidos_cambio = False
			es_error_manual = False
			msg_negocio = ""

			if estado_objetivo == "APROBADO":
				if estado_actual in ("RETIRADO", "ELIMINADO","CONCLUYO"):
					es_error_manual = True
					msg_negocio = "No permitido: se pidió APROBADO pero el estado actual es {}".format(estado_actual_raw)
				elif estado_actual == "APROBADO":
					msg_ok = "Sin cambios: {} ya estaba en APROBADO".format(codigo)
					print("[RPA]", msg_ok)
					resultado.estado = 1
					resultado.mensaje_error = msg_ok
					return resultado
				else:
					permitidos_cambio = True

			elif estado_objetivo == "DESAPROBADO":
				if estado_actual == "DESAPROBADO":
					msg_ok = "Sin cambios: {} ya estaba en DESAPROBADO".format(codigo)
					print("[RPA]", msg_ok)
					resultado.estado = 1
					resultado.mensaje_error = msg_ok
					return resultado

				if estado_actual == "MATRICULADO":
					permitidos_cambio = True
				elif estado_actual in ("APROBADO", "CONCLUYO", "RETIRADO", "ELIMINADO"):
					es_error_manual = True
					msg_negocio = "No permitido: se pidió DESAPROBADO pero el estado actual es {}".format(estado_actual_raw)
				else:
					es_error_manual = True
					msg_negocio = "Estado actual no contemplado para DESAPROBADO: {}".format(estado_actual_raw)


			elif estado_objetivo == "CONCLUYO":
				if estado_actual == "CONCLUYO":
					msg_ok = "Sin cambios: {} ya estaba en CONCLUYO".format(codigo)
					print("[RPA]", msg_ok)
					resultado.estado = 1
					resultado.mensaje_error = msg_ok
					return resultado
				
				else:
					permitidos_cambio = True
				

			if es_error_manual:
				print("[RPA][WARN]", msg_negocio)
				resultado.estado = 2
				resultado.mensaje_error = msg_negocio
				return resultado

			if permitidos_cambio:
				if select_el is None:
					msg = "No se puede cambiar a '{}': la fila no es editable (estado actual='{}').".format(estado_final, estado_actual_raw)
					print("[RPA][WARN]", msg)
					resultado.estado = 2
					resultado.mensaje_error = msg
					return resultado

				sel = Select(select_el)

				ok_sel = _select_estado(sel, estado_final)
				if not ok_sel:
					msg = "No existe opción '{}' en el combo de estado para el código {}.".format(estado_final, codigo)
					print("[RPA][WARN]", msg)
					resultado.estado = 2
					resultado.mensaje_error = msg
					return resultado

				print("[RPA] {}: {} -> {}".format(codigo, estado_actual_raw, estado_final))

				boton_grabar = wait.until(
					EC.element_to_be_clickable((
						By.XPATH,
						"//button[contains(@class,'pucpBoton') and contains(@onclick,'grabar') and normalize-space()='Grabar']"
					))
				)
				boton_grabar.click()
				time.sleep(1)

				try:
					alert_obj = WebDriverWait(driver, 5).until(EC.alert_is_present())
					print("[RPA] Alert:", alert_obj.text)
					alert_obj.accept()  
					time.sleep(1)

					try:
						alert_obj2 = WebDriverWait(driver, 2).until(EC.alert_is_present())
						print("[RPA] Alert 2:", alert_obj2.text)
						alert_obj2.accept()
						time.sleep(1)
					except TimeoutException:
						pass

				except TimeoutException:
					pass



				msg_ok = "Cambio OK: {} {} -> {}".format(codigo, estado_actual_raw, estado_final)
				print("[RPA]", msg_ok)
				resultado.estado = 1
				resultado.mensaje_error = msg_ok
				return resultado


			msg = "No se ejecutó acción para {} (actual='{}', objetivo='{}').".format(codigo, estado_actual_raw, estado_final)
			print("[RPA][WARN]", msg)
			resultado.estado = 2
			resultado.mensaje_error = msg
			return resultado

		except TimeoutException:
			msg = "Timeout: no se encontró la fila del código {} o no cargó edición.".format(codigo)
			print("[RPA][ERROR]", msg)
			resultado.estado = 2
			resultado.mensaje_error = msg
			return resultado

		except Exception as e:
			msg = "Error en asignarEstadoFinal ({}): {}".format(codigo, e)
			print("[RPA][ERROR]", msg)
			resultado.estado = 2
			resultado.mensaje_error = msg
			return resultado
		
	def clickBotonGenerarVistaPreviaCertificado(self, url_get="", driver="", tipo_programa=""):

		wait = WebDriverWait(driver, 10)

		
		if not url_get or not driver:
			return self.rpa_fail("Parámetros inválidos: url_get/driver vacíos.")

		try:
			driver.get(self.url_eros)
			time.sleep(1)
			driver.get(self.url_eros)
			time.sleep(1)
			driver.get(self.url_eros)
			time.sleep(2)
			driver.get(url_get)
			time.sleep(2)
			print("[RPA] URL programa:", driver.current_url)

			if tipo_programa == "diplomatura":
				xpath_boton = (
					"//button[normalize-space()='Generar vista previa' "
    				"and contains(@onclick, \"generarCertificaciones('1 '\") ]"
				)
			else:
				xpath_boton = (
					"//button[normalize-space()='Generar vista previa' "
					"and contains(@onclick, \"generarCertificaciones('3 '\") ]"
				)
				print(xpath_boton)

			boton = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton)))
			driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton)

			boton.click()
			time.sleep(1)
			self.aceptar_alertas(driver)

			return self.rpa_ok("OK: botón 'Generar vista previa' clickeado para el programa.")

		except TimeoutException as e:
			return self.rpa_fail("Timeout: no se encontró el botón 'Generar vista previa' del programa.", e)

		except Exception as e:
			return self.rpa_fail("Error en clickBotonGenerarVistaPreviaCertificado", e)

	def generarVistaPreviaCertificados(self, driver="", codigo="", clave_programa="", id_archivo=""):

		wait = WebDriverWait(driver, 10)

		codigo = str(codigo).strip()
		id_archivo = str(id_archivo).strip()
		clave_programa = str(clave_programa).strip()


		def esperar_descarga(ruta, archivos_antes, t0, timeout_s=60):
			while (time.time() - t0) < timeout_s:
				actuales = set(os.listdir(ruta))
				nuevos = [a for a in (actuales - archivos_antes) if not a.endswith(".crdownload")]
				if nuevos:
					return nuevos[0]
				time.sleep(1)

			candidatos = []
			for a in os.listdir(ruta):
				if a.lower().endswith(".pdf"):
					p = os.path.join(ruta, a)
					try:
						if os.path.getmtime(p) >= (t0 - 2):
							candidatos.append(a)
					except Exception:
						pass

			if candidatos:
				candidatos.sort(key=lambda x: os.path.getmtime(os.path.join(ruta, x)), reverse=True)
				return candidatos[0]

			return ""
		
		if not driver or not codigo:
			return self.rpa_fail("Parámetros inválidos: driver/codigo vacíos.")

		try:
			
			xpath_fila = (
				"//table//tbody//tr[normalize-space(td[1])='{0}' "
				"or normalize-space(td[1]//a)='{0}']"
			).format(codigo)

			fila = wait.until(EC.presence_of_element_located((By.XPATH, xpath_fila)))
			driver.execute_script("arguments[0].scrollIntoView({block:'center'});", fila)
			print("[RPA] Fila encontrada para participante:", codigo)

			codigo_en_fila = fila.find_element(By.XPATH, ".//td[1]").text.strip()
			if codigo_en_fila != codigo:
				return self.rpa_fail(
					"Seguridad: la fila encontrada no coincide. Esperado={}, encontrado={}".format(codigo, codigo_en_fila)
				)

			
			try:
				link_vista_previa = fila.find_element(By.XPATH, ".//a[.//img[contains(@src,'i_vistaprevia')]]")
			except Exception:
				link_vista_previa = None

			if link_vista_previa is None:
				try:
					link_vista_previa = fila.find_element(By.XPATH, ".//a[contains(@href,\"javascript:descargar(\")]")
				except Exception:
					link_vista_previa = None

			if link_vista_previa is None:
				return self.rpa_fail("No se encontró el enlace de vista previa/descargar para el código {}".format(codigo))

			href = (link_vista_previa.get_attribute("href") or "").strip()
			print("[RPA] Link vista previa encontrado:", href)

		
			
			identidad_dir = id_archivo.replace("/", "_").replace("\\", "_")
			ruta_descarga = os.path.abspath(os.path.join("precisam", "certificados", identidad_dir))

			try:
				os.makedirs(ruta_descarga, exist_ok=True)
			except Exception as e:
				return self.rpa_fail("No se pudo crear carpeta de descarga '{}'".format(ruta_descarga), e)

			try:
				driver.execute_cdp_cmd("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": ruta_descarga})
				print("[RPA] Descargas habilitadas. Carpeta:", ruta_descarga)
			except Exception as e:
				print("[RPA][WARN] No se pudo habilitar descargas por CDP:", e)

			base_nombre = "{}_{}".format(clave_programa.strip(), str(id_archivo).strip())
			nombre_final = "{}.pdf".format(base_nombre)
			destino_final = os.path.join(ruta_descarga, nombre_final)

			if os.path.exists(destino_final):
				try:
					os.remove(destino_final)
					print("[RPA] Archivo existente eliminado para reemplazar:", destino_final)
				except Exception as e:
					return self.rpa_fail("No se pudo eliminar el archivo existente {}".format(destino_final), e)

			
			archivos_antes = set(os.listdir(ruta_descarga))
			driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link_vista_previa)

			t0 = time.time()
			link_vista_previa.click()
			time.sleep(1)
			self.aceptar_alertas(driver)

			archivo_descargado = esperar_descarga(ruta_descarga, archivos_antes, t0, timeout_s=60)
			if not archivo_descargado:
				return self.rpa_fail("No se detectó la descarga del PDF para {} (identidad='{}').".format(identidad_dir))

			
			origen = os.path.join(ruta_descarga, archivo_descargado)

			try:
				if os.path.exists(destino_final):
					os.remove(destino_final)
				if os.path.abspath(origen) != os.path.abspath(destino_final):
					os.rename(origen, destino_final)
			except Exception as e:
				return self.rpa_fail("No se pudo reemplazar el archivo final {}".format(destino_final), e)

			print("[RPA] Vista previa descargada OK:", destino_final)

			
			file_path_bucket = "certificados/{}".format(identidad_dir)
			uuid = nombre_final

			try:
				with open(destino_final, "rb") as f:
					ok_upload = self.uploadFileToAWS3(f, file_path_bucket, uuid)

				if not ok_upload:
					return self.rpa_fail("Se descargó el PDF pero FALLÓ el upload a AWS: {}/{}".format(file_path_bucket, uuid))

				print("[RPA] Upload AWS OK:", "{}/{}".format(file_path_bucket, uuid))

				try:
					if os.path.isdir(ruta_descarga):
						shutil.rmtree(ruta_descarga)
						print("[RPA] Carpeta eliminada:", ruta_descarga)
				except Exception as e:
					return self.rpa_fail("Upload OK, pero no se pudo eliminar la carpeta {}".format(ruta_descarga), e)

				try:
					chk = fila.find_element(
						By.XPATH,
						".//input[@type='checkbox' and contains(@onclick,'setearCodCertificado')]"
					)

					driver.execute_script("arguments[0].scrollIntoView({block:'center'});", chk)

					if not chk.is_selected():
						chk.click()

					print("[RPA] Checkbox marcada (value={}): {}".format(chk.get_attribute("value"), chk.is_selected()))

					btn_eliminar = wait.until(
						EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Eliminar' and contains(@onclick,'eliminar')]"))
					)
					driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_eliminar)
					btn_eliminar.click()
					time.sleep(1)

					self.aceptar_alertas(driver)

					try:
						wait.until(EC.staleness_of(fila))
					except Exception:
						pass

					print("[RPA] Eliminación ejecutada OK en pantalla.")

				except Exception as e:
					return self.rpa_fail("Upload OK, pero falló marcar checkbox / eliminar en pantalla", e)



			except Exception as e:
				return self.rpa_fail("Error subiendo a AWS ({})".format(uuid), e)

			return self.rpa_ok("OK: descargado y subido a AWS: {}/{}".format(file_path_bucket, uuid))

		except TimeoutException:
			return self.rpa_fail("Timeout: no se encontró el botón/fila/link para el código {}".format(codigo))

		except Exception as e:
			return self.rpa_fail("Error en generarVistaPreviaCertificados ({})".format(codigo), e)


	def calificarPromedioFinalAntesDePublicar(self, driver="", tipo_proceso="", identifica_proceso="", codigo="", clave_programa=""):
		wait = WebDriverWait(driver, 30)

		tipo_proceso = str(tipo_proceso).strip()
		identifica_proceso = str(identifica_proceso).strip()
		codigo = str(codigo).strip()
		clave_programa = str(clave_programa).strip()

		if not driver or not tipo_proceso or not identifica_proceso:
			return self.rpa_fail(
				"Parametros invalidos para paso previo de notas. "
				"tipo_proceso='{}', identifica_proceso='{}', codigo='{}', programa='{}'".format(
					tipo_proceso, identifica_proceso, codigo, clave_programa
				)
			)

		url_notas = (
			f"{self.url_ares}/pucp/notaesp/newevalu/newevalu"
			"?accion=Ingresar"
			"&tipoProceso={}"
			"&identificaProceso={}"
		).format(tipo_proceso, identifica_proceso)

		try:
			print("[RPA][NOTAS] Ingreso a Notas para codigo={} programa={} URL={}".format(codigo, clave_programa, url_notas))
			driver.get(url_notas)
			time.sleep(2)
			norm_chars_from = "ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚabcdefghijklmnopqrstuvwxyzáéíóú"
			norm_chars_to = "abcdefghijklmnopqrstuvwxyzaeiouabcdefghijklmnopqrstuvwxyzaeiou"
			xpath_txt_norm = "translate(normalize-space(.), '{}', '{}')".format(norm_chars_from, norm_chars_to)

			try:
				link_calculo = wait.until(
					EC.element_to_be_clickable((By.XPATH, "//a[contains({}, 'calculo del promedio final')]".format(xpath_txt_norm)))
				)
			except Exception:
				try:
					link_calculo = wait.until(
						EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'calculoPromedio') or contains(@onclick,'calculoPromedio')]"))
					)
				except Exception as e_link:
					return self.rpa_fail(
						"No se encontro enlace 'Calculo del promedio final' para codigo={} programa={} (URL actual={})".format(
							codigo, clave_programa, driver.current_url
						),
						e_link
					)

			driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link_calculo)
			link_calculo.click()
			print("[RPA][NOTAS] Abierto 'Calculo del promedio final' para codigo={}".format(codigo))
			time.sleep(2)

			try:
				btn_calificar = wait.until(
					EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Calificar']"))
				)
			except Exception:
				try:
					btn_calificar = wait.until(
						EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick,'calcularPromedio')]"))
					)
				except Exception as e_btn:
					return self.rpa_fail(
						"No se encontro boton 'Calificar' para codigo={} programa={} (URL actual={})".format(
							codigo, clave_programa, driver.current_url
						),
						e_btn
					)

			driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_calificar)
			btn_calificar.click()
			print("[RPA][NOTAS] Click en 'Calificar' para codigo={}".format(codigo))
			time.sleep(2)
			self.aceptar_alertas(driver)
			time.sleep(1)

			xpath_titulo_ok = "//*[contains({}, 'calculo del promedio final')]".format(xpath_txt_norm)
			xpath_msg_ok = "//*[contains({}, 'los promedios finales han sido actualizados satisfactoriamente.')]".format(xpath_txt_norm)
			xpath_link_resultados_ok = "//*[contains({}, 'haga clic aqui para ver los resultados.')]".format(xpath_txt_norm)

			try:
				wait.until(EC.presence_of_element_located((By.XPATH, xpath_titulo_ok)))
				wait.until(EC.presence_of_element_located((By.XPATH, xpath_msg_ok)))
				wait.until(EC.presence_of_element_located((By.XPATH, xpath_link_resultados_ok)))
				print("[RPA][NOTAS] Confirmacion de calculo validada para codigo={}".format(codigo))
			except Exception as e_confirm:
				return self.rpa_fail(
					"No se pudo validar confirmacion de exito tras 'Calificar' para codigo={} programa={} (URL actual={})".format(
						codigo, clave_programa, driver.current_url
					),
					e_confirm
				)

			print("[RPA][NOTAS] Paso previo completado. Continuando a publicacion para codigo={}".format(codigo))
			return self.rpa_ok("[NOTAS] Paso previo Notas OK para codigo={} programa={}".format(codigo, clave_programa))

		except TimeoutException as e:
			return self.rpa_fail(
				"Timeout en paso previo de Notas para codigo={} programa={} (URL actual={})".format(
					codigo, clave_programa, driver.current_url
				),
				e
			)
		except Exception as e:
			return self.rpa_fail(
				"Error en paso previo de Notas para codigo={} programa={} (URL actual={})".format(
					codigo, clave_programa, driver.current_url
				),
				e
			)
	
	def publicarCertificados(self, url_get="", driver="", codigo="", clave_programa="", tipo_programa="", tipo_proceso="", identifica_proceso=""):

		wait = WebDriverWait(driver, 10)

		codigo = str(codigo).strip()
		clave_programa = str(clave_programa).strip()
		tipo_proceso = str(tipo_proceso).strip()
		identifica_proceso = str(identifica_proceso).strip()

		if not url_get or not driver or not codigo:
			return self.rpa_fail("Parámetros inválidos: url_get/driver/codigo vacíos.")

		try:
			res_notas = self.calificarPromedioFinalAntesDePublicar(
				driver=driver,
				tipo_proceso=tipo_proceso,
				identifica_proceso=identifica_proceso,
				codigo=codigo,
				clave_programa=clave_programa
			)
			if res_notas is not None and getattr(res_notas, "error", 0) == 1:
				return self.rpa_fail(res_notas.mensaje_error)

			print("[RPA] Paso previo de Notas exitoso. Continuando publicacion de certificado...")
			
			driver.get(self.url_ares)
			time.sleep(2)
			driver.get(self.url_ares)
			time.sleep(2)
			driver.get(url_get)
			time.sleep(3)
			print("[RPA] URL:", driver.current_url)

			xpath_fila = (
				"//table//tbody//tr[normalize-space(td[1])='{0}' "
				"or normalize-space(td[1]//a)='{0}']"
			).format(codigo)

			fila = wait.until(EC.presence_of_element_located((By.XPATH, xpath_fila)))
			driver.execute_script("arguments[0].scrollIntoView({block:'center'});", fila)
			print("[RPA] Fila encontrada para participante:", codigo)

			codigo_en_fila = fila.find_element(By.XPATH, ".//td[1]").text.strip()
			if codigo_en_fila != codigo:
				return self.rpa_fail(
					"Seguridad: la fila encontrada no coincide. Esperado={}, encontrado={}".format(codigo, codigo_en_fila)
				)

			try:
				if tipo_programa == "diplomatura":

						chk = fila.find_element(
							By.XPATH,
							".//input[@type='checkbox' and starts-with(normalize-space(@name),'chkCerti1')]"
						)
				else:
					chk = fila.find_element(
						By.XPATH,
						".//input[@type='checkbox' and starts-with(normalize-space(@name),'chkCerti3')]"
					)

			except Exception:
				print("[RPA] No se encontró chkCerti1. Clickeando 'Generar vista previa' y reintentando...")

				res_prev = self.clickBotonGenerarVistaPreviaCertificado(url_get=url_get, driver=driver, tipo_programa=tipo_programa)

				if res_prev is not None and getattr(res_prev, "error", 0) == 1:
					return self.rpa_fail(res_prev.mensaje_error)

				try:
					time.sleep(2)

					fila = wait.until(EC.presence_of_element_located((By.XPATH, xpath_fila)))
					driver.execute_script("arguments[0].scrollIntoView({block:'center'});", fila)

					if tipo_programa == "diplomatura":

						chk = fila.find_element(
							By.XPATH,
							".//input[@type='checkbox' and starts-with(normalize-space(@name),'chkCerti1')]"
						)
					else:
						chk = fila.find_element(
							By.XPATH,
							".//input[@type='checkbox' and starts-with(normalize-space(@name),'chkCerti3')]"
						)

				except Exception as e2:
					return self.rpa_fail(
						"No se encontró checkbox chkCerti1 en la fila del código {} incluso luego de generar vista previa".format(codigo),
						e2
					)

			driver.execute_script("arguments[0].scrollIntoView({block:'center'});", chk)
			if not chk.is_selected():
				chk.click()

			print("[RPA] Checkbox marcada (value={}): {}".format(chk.get_attribute("value"), chk.is_selected()))

			try:
				btn_publicar = wait.until(
					EC.element_to_be_clickable((
						By.XPATH,
						"//button[normalize-space()='Publicar' and contains(@onclick,'publicar')]"
					))
				)
				driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_publicar)
				btn_publicar.click()
				time.sleep(3)
				self.aceptar_alertas(driver)

				wait.until(EC.staleness_of(fila))

				msg_ok = "Publicado OK: {}{}".format(
					codigo,
					(" ({})".format(clave_programa) if clave_programa else "")
				)
				return self.rpa_ok(msg_ok)

			except TimeoutException as e:
				return self.rpa_fail(
					"Timeout: no se pudo confirmar la publicación del código {}".format(codigo),
					e
				)
			except Exception as e:
				return self.rpa_fail(
				"Error en publicarCertificados ({})".format(codigo),
				e
			)

		except Exception as e:
			return self.rpa_fail(
				"Error en publicarCertificados ({})".format(codigo),
				e
			)

	def uploadFileToAWS3(self, file, filePath, uuid):
		try:
			media_storage = MediaStorage()
			file_path_within_bucket = os.path.join(filePath, uuid)

			print("[RPA] Bucket:", getattr(media_storage, "bucket_name", None))
			print("[RPA] Location:", getattr(media_storage, "location", None))
			print("[RPA] Key final:", file_path_within_bucket)

			media_storage.save(file_path_within_bucket, file)
			return True
		except Exception as e:
			print("[RPA][ERROR] uploadFileToAWS3 exception:", repr(e))
			return False
		
	def rpa_fail(self, msg, exc=None):
		resultado = ResultadoRPA()
		if exc is not None:
			msg = "{}: {}".format(msg, exc)
		print("[RPA][ERROR]", msg)
		resultado.estado = 2
		resultado.error = 1
		resultado.mensaje_error = msg
		resultado.continua = False
		return resultado

	def rpa_ok(self, msg):
		resultado = ResultadoRPA()
		print("[RPA]", msg)
		resultado.estado = 1
		resultado.error = 0
		resultado.mensaje_error = msg
		resultado.continua = True
		return resultado

	def aceptar_alertas(self, driver, timeout_1=5, timeout_2=2):
		try:
			alert_obj = WebDriverWait(driver, timeout_1).until(EC.alert_is_present())
			print("[RPA] Alert:", alert_obj.text)
			alert_obj.accept()
			time.sleep(1)

			try:
				alert_obj2 = WebDriverWait(driver, timeout_2).until(EC.alert_is_present())
				print("[RPA] Alert 2:", alert_obj2.text)
				alert_obj2.accept()
				time.sleep(1)
			except TimeoutException:
				pass

		except TimeoutException:
			pass

	def closeCampusVirtual(self, driver=None):
		if driver is None:
			return
		try:
			driver.quit()  
			print("[RPA] Driver cerrado (quit).")
		except Exception as e:
			print("[RPA][WARN] No se pudo cerrar driver con quit:", e)
			try:
				driver.close()
			except Exception:
				pass
	
	
	
	def _leer_fechas_actividad(self, driver, wait):

		x_inicio = (
			"//td[contains(@class,'pucpCriterio') "
			"and contains(normalize-space(.),'Fecha de inicio')]"
			"/following-sibling::td[contains(@class,'pucpValor')][1]"
		)

		x_fin = (
			"//td[contains(@class,'pucpCriterio') "
			"and contains(normalize-space(.),'Fecha de fin')]"
			"/following-sibling::td[contains(@class,'pucpValor')][1]"
		)

		ini_el = wait.until(EC.visibility_of_element_located((By.XPATH, x_inicio)))
		fin_el = wait.until(EC.visibility_of_element_located((By.XPATH, x_fin)))

		ini_txt = ini_el.text.strip()
		fin_txt = fin_el.text.strip()

		return ini_txt, fin_txt

	def _parse_fecha(self, value):
		try:
			if value is None:
				return None
			if hasattr(value, "date"):
				return value.date()
			if isinstance(value, str):
				if '/' in value:
					return datetime.strptime(value.strip(), "%d/%m/%Y").date()
				return datetime.strptime(value.strip()[:10], "%Y-%m-%d").date()
		except Exception:
			return None

	def validarFechasActividad( self, driver, codigo_programa, fecha_inicio_dt, fecha_fin_dt, url_get=None,enviar_correo=True, programa='', conf_cambiofecha="", ci=''):
		
		if not driver:
			return self.rpa_fail("Parámetros inválidos: driver vacío para validarFechasActividad.")
		if not url_get:
			return self.rpa_fail("Parámetros inválidos: url_get vacío para validarFechasActividad.")
		
		driver.get(self.url_eros)
		time.sleep(3)
		driver.get(url_get)
		time.sleep(4)

		resultado = ResultadoRPA()

		try:

			wait = WebDriverWait(driver, 10)
			
			campus_ini_txt, campus_fin_txt = self._leer_fechas_actividad(driver, wait)
			
			
			campus_ini = self._parse_fecha(campus_ini_txt)
			campus_fin = self._parse_fecha(campus_fin_txt)
			print('Fechas Campus Virtual:',campus_ini, campus_fin)
			
			bd_ini = self._parse_fecha(fecha_inicio_dt) if fecha_inicio_dt else None
			bd_fin = self._parse_fecha(fecha_fin_dt) if fecha_fin_dt else None
			print('Fechas Ultimo Horario Registrado:',bd_ini, bd_fin)
			
			# Todas las fechas requeridas deben existir y parsear correctamente (dd/mm/yyyy)
			
			if not (bd_ini and bd_fin and campus_ini and campus_fin):
				detalle = []
				if not campus_ini:
					detalle.append("fecha_inicio_campus")
				if not campus_fin:
					detalle.append("fecha_fin_campus")
				if not bd_ini:
					detalle.append("fecha_inicio_bd")
				if not bd_fin:
					detalle.append("fecha_fin_bd")

				return self.rpa_fail(
					"Fechas requeridas faltantes o inválidas (formato esperado dia/mes/año): {}".format(
						", ".join(detalle)
					)
				)
			
			if campus_ini == bd_ini and campus_fin == bd_fin:
				print('Validado : Fechas correctas')
				try:
					ci.registrarCambioFechasRpaLog(
						codigo_programa=str(codigo_programa or "").strip(),
						conf_cambiofecha="1",
						mensaje="Fechas ahora coinciden en Campus vs BD. Cambio de estado conf_cambiofecha"
					)
					print("[RPA][CAMBIO_FECHA] Estado conf_cambiofecha actualizado: 2 -> 1")
					resultado.estado = 1
					resultado.error = 0
					resultado.continua = True
					resultado.mensaje_error = None
				except Exception as e_log:
					resultado.estado = 2
					resultado.error = 1
					resultado.continua = False
					resultado.mensaje_error = "[RPA][CAMBIO_FECHA][WARN] No se pudo actualizar conf_cambiofecha "
					print("[RPA][CAMBIO_FECHA][WARN] No se pudo actualizar conf_cambiofecha 2 -> 1:", e_log)
				
				return resultado
			else:
				'''
				print('Validacion : Fechas Incorrectas, Se procede a enviar correo')
				msg = (
					"No se continuó el proceso por error en las fechas. "
					f"Campus({campus_ini_txt} - {campus_fin_txt}) "
					f"vs BD({fecha_inicio_dt} - {fecha_fin_dt})"
				)
				conf_cambiofecha_norm = str(conf_cambiofecha).strip()
				
				if enviar_correo and conf_cambiofecha_norm!='2':
					
					fmt = "%d/%m/%Y"

					campus_ini_mail = campus_ini.strftime(fmt)
					campus_fin_mail = campus_fin.strftime(fmt)
					bd_ini_mail = bd_ini.strftime(fmt)
					bd_fin_mail = bd_fin.strftime(fmt)
					
					self.enviarCorreoFechasDistintas(
						codigo_programa=programa,
						campus_ini=campus_ini_mail,
						campus_fin=campus_fin_mail,
						dt_ini=bd_ini_mail,
						dt_fin=bd_fin_mail
					)

				resultado.estado = 0
				resultado.error = 1
				resultado.continua = False
				resultado.mensaje_error = msg
				return resultado
				'''
				
				print('Validacion : Fechas Incorrectas, Se procede a ejecutar cambio de fechas')
				msg = (
					"Se detectaron fechas distintas y se intentara registrar el cambio de fechas. "
					f"Campus({campus_ini_txt} - {campus_fin_txt}) "
					f"vs BD({fecha_inicio_dt} - {fecha_fin_dt})"
				)

				#fmt = "%m/%d/%Y"
				fmt = "%d/%m/%Y"
				'''
				fecha_inicio_dice = campus_ini.strftime(fmt)
				fecha_inicio_debe_decir = bd_ini.strftime(fmt)
				fecha_fin_dice = campus_fin.strftime(fmt)
				fecha_fin_debe_decir = bd_fin.strftime(fmt)
				'''
				fecha_inicio_dice = campus_ini.strftime(fmt).replace("/0", "/").lstrip("0")
				fecha_fin_dice = campus_fin.strftime(fmt).replace("/0", "/").lstrip("0")

				fecha_inicio_debe_decir = bd_ini.strftime(fmt).replace("/0", "/").lstrip("0")
				fecha_fin_debe_decir = bd_fin.strftime(fmt).replace("/0", "/").lstrip("0")

				fmt = "%d/%m/%Y"
				'''
				fecha_correo_ini_dice = campus_ini.strftime(fmt).replace("/0", "/").lstrip("0")
				fecha_correo_fin_dice = campus_fin.strftime(fmt).replace("/0", "/").lstrip("0")

				fecha_correo_ini_debe = bd_ini.strftime(fmt).replace("/0", "/").lstrip("0")
				fecha_correo_fin_debe = bd_fin.strftime(fmt).replace("/0", "/").lstrip("0")
				print(fecha_correo_ini_dice,fecha_correo_fin_dice,fecha_correo_ini_debe,fecha_correo_fin_debe)
				'''

				
				fecha_correo_ini_dice = campus_ini.strftime(fmt)
				fecha_correo_fin_dice =  campus_fin.strftime(fmt)

				fecha_correo_ini_debe = bd_ini.strftime(fmt)
				fecha_correo_fin_debe = bd_fin.strftime(fmt)
				
				
				conf_cambiofecha_norm = str(conf_cambiofecha).strip()
				print('hora',conf_cambiofecha_norm)
				if conf_cambiofecha_norm in ("2"):
					print("[RPA][CAMBIO_FECHA] Ya existe estado previo de cambio de fecha (conf_cambiofecha={}). Se omite nuevo intento.".format(conf_cambiofecha_norm))
					resultado.estado = 2
					resultado.error = 0
					resultado.continua = False
					resultado.mensaje_error = (
						"Se omitió el reenvío por estado previo de cambio de fecha (conf_cambiofecha={}).".format(conf_cambiofecha_norm)
					)
					return resultado
				
				if conf_cambiofecha_norm not in ("", "0", "1", "2"):
					print("[RPA][WARN] conf_cambiofecha no reconocido '{}'. Se continuará con flujo de intento.".format(
						conf_cambiofecha_norm
					))


				print(msg)
				
				ejecutar_cambio_fechas_main(
					campus_conn=self,
					codigo_programa=str(codigo_programa or "").strip(),
					programa=programa,
					fecha_inicio_dice=fecha_inicio_dice,
					fecha_inicio_debe_decir=fecha_inicio_debe_decir,
					fecha_fin_dice=fecha_fin_dice,
					fecha_fin_debe_decir=fecha_fin_debe_decir,
					fecha_correo_ini_dice=fecha_correo_ini_dice,
					fecha_correo_fin_dice=fecha_correo_fin_dice,
					fecha_correo_ini_debe=fecha_correo_ini_debe,
					fecha_correo_fin_debe=fecha_correo_fin_debe
				)
				resultado.estado = 2
				resultado.error = 0
				resultado.continua = False
				resultado.mensaje_error = (
					"Se omitió el reenvío por estado previo de cambio de fecha (conf_cambiofecha={}).".format(conf_cambiofecha_norm)
				)
				return resultado
				
				
				
			
		except Exception as e:
			msg = f"Error al validar fechas en Campus Virtual: {e}"
			print("[RPA][ERROR]", msg)
			
			resultado.estado = 0
			resultado.error = 1
			resultado.continua = False
			resultado.mensaje_error = msg
			
			return resultado	
	
	def _norm(self, txt):
		
		if not txt:
			return ""
		return (
			txt.replace('\n', ' ')
			.replace('\r', ' ')
			.strip()
			.upper()
		)
	
	def configurarCertificacionDigitalCampusVirtual(self, url_get='', driver=''):

		resultado = ResultadoRPA()

		try:
			print("[RPA] Iniciando configuración de certificación digital")

			driver.get(url_get)
			time.sleep(3)
			wait = WebDriverWait(driver, 10)

			# Intentar entrar a modo edición (si aplica)
			try:
				print("[RPA] Buscando botón Editar")
				boton_editar = wait.until(
					EC.element_to_be_clickable((
						By.XPATH,
						"//button[normalize-space(.)='Editar' and contains(@onclick,'editar')]"
					))
				)
				boton_editar.click()
				print("[RPA] Click en botón Editar")
			except Exception:
				print("[RPA] Botón Editar no disponible")
				pass

			time.sleep(10)

			# Tabla de configuración (por headers exactos)
			tabla = wait.until(EC.presence_of_element_located((
				By.XPATH,
				"//table[.//td[contains(@class,'pucpCeldaTitulo') and contains(normalize-space(.),'Habilitar')]"
				" and .//td[contains(@class,'pucpCeldaTitulo') and contains(normalize-space(.),'Tipo de certificación')]"
				" and .//td[contains(@class,'pucpCeldaTitulo') and contains(normalize-space(.),'Estados finales')]]"
			)))
			print("[RPA] Tabla de configuración encontrada")

			header_tr = tabla.find_element(By.XPATH, ".//tr[td[contains(@class,'pucpCeldaTitulo')]]")
			header_tds = header_tr.find_elements(By.XPATH, "./td[contains(@class,'pucpCeldaTitulo')]")
			headers = [td.text.strip() for td in header_tds]

			print("[RPA] Headers detectados:")
			for i, h in enumerate(headers):
				print(f"  [{i}] {h}")

			def col_idx(texto):
				t = (texto or "").lower()
				for i, h in enumerate(headers):
					if t in (h or "").lower():
						return i
				return None

			idx_hab = col_idx("Habilitar")
			idx_tipo = col_idx("Tipo de certificación")
			idx_est = col_idx("Estados finales disponibles")
			idx_pri = col_idx("Generar para la actividad principal")
			idx_notas = col_idx("Generar cuando todas las notas estén registradas")

			# "Mostrar fechas de la actividad"
			idx_fecha = col_idx("Mostrar fechas de la actividad")
			if idx_fecha is None:
				for i, td in enumerate(header_tds):
					if td.find_elements(By.XPATH, ".//a[contains(@href,'MOSTRAR FECHAS ACTIVIDAD')]"):
						idx_fecha = i
						break

			print("[RPA] Indices de columnas:")
			print("  idx_hab   =", idx_hab)
			print("  idx_tipo  =", idx_tipo)
			print("  idx_est   =", idx_est)
			print("  idx_pri   =", idx_pri)
			print("  idx_fecha =", idx_fecha)
			print("  idx_notas =", idx_notas, "(Se ignora)")
			
			if idx_notas is not None:
				print("[RPA] Columna 'Generar cuando todas las notas esten registradas' presente: Se Ignora.")
			
			# columna opcional 
			if idx_pri is None:
				print("[RPA] Columna 'Generar para la actividad principal' NO existe (OK, se omite en todas las filas)")

			# Filas de datos
			filas_all = tabla.find_elements(By.XPATH, ".//tr[td and not(td[contains(@class,'pucpCeldaTitulo')])]")
			print("[RPA] Filas detectadas")

			# Detectar diplomatura segun filas habilitadas
			es_diplomatura = False
			print("[RPA] Iniciando detección de diplomatura")

			for f in filas_all:
				chk_hab = f.find_elements(By.XPATH, ".//input[@type='checkbox' and starts-with(@name,'chkReq')]")
				if not chk_hab:
					continue
				if not chk_hab[0].is_selected():
					continue

				tds = f.find_elements(By.XPATH, "./td")
				if not tds:
					continue
				
				# Detectar columna extra (Nro) al inicio
				offset = 0
				cls0 = (tds[0].get_attribute("class") or "")
				if "pucpNro" in cls0:
					offset = 1

				if idx_tipo is not None and (idx_tipo + offset) < len(tds):
					tipo_text = self._norm(tds[idx_tipo + offset].text)
					if "DIPLOMA" in tipo_text:
						print("[RPA] Fila diplomatura detectada")
						es_diplomatura = True
						break
			
			if es_diplomatura:
				print("[RPA] Proceso identificado como DIPLOMATURA")
			else:
				print("[RPA] Proceso identificado como NO DIPLOMATURA")

			procesadas = 0
			print("[RPA] Iniciando configuración por filas habilitadas")

			for fila in filas_all:

				# solo filas habilitadas (chkReq marcado)
				chk_hab = fila.find_elements(
					By.XPATH,
					".//input[@type='checkbox' and starts-with(@name,'chkReq')]"
				)

				if not chk_hab:
					# No es fila de configuración
					continue

				if not chk_hab[0].is_selected():
					# Fila no habilitada (no marcada)
					continue

				# Ya que pasa el filtro, recién leemos celdas
				tds = fila.find_elements(By.XPATH, "./td")
				if not tds:
					continue

				# Tipo de certificación 
				tipo_cert = ""
				if idx_tipo is not None and (idx_tipo + offset) < len(tds):
					tipo_cert = self._norm(tds[idx_tipo + offset].text)

				print("[RPA] Procesando fila")

				# ESTADOS FINALES
				if idx_est is not None and  (idx_est + offset) < len(tds):
					celda_est = tds[idx_est + offset]

					# Diplomatura: "CONCLUYÓ" (value=5)
					if es_diplomatura:
						desired_value = "5"
					else:
						# No diplomatura: Constancia -> DESAPROBADO (value=2), otros -> CONCLUYÓ (value=5)
						if "CONSTANCIA DE PARTICIPACIÓN" in tipo_cert:
							desired_value = "2"
						else:
							desired_value = "5"

					print(f"[RPA] Estado final esperado")

					chk_obj = celda_est.find_elements(By.XPATH, f".//input[@type='checkbox' and @value='{desired_value}']")
					if chk_obj:
						c = chk_obj[0]

						if c.is_selected():
							print("[RPA] Estado final ya estaba marcado (OK)")

						elif c.get_attribute("disabled") is not None:
							print("[RPA] Estado final bloqueado y marcado por el sistema (OK)")

						else:
							c.click()
							time.sleep(0.2)
							print("[RPA] Estado final marcado por RPA")
					else:
						print("[RPA] No se encontró checkbox de estado final con value esperado")

				# GENERAR PARA LA ACTIVIDAD PRINCIPAL
				if idx_pri is not None and (idx_pri + offset) < len(tds):
					celda_pri = tds[idx_pri + offset]
					chk_pri = celda_pri.find_elements(By.XPATH, ".//input[@type='checkbox']")
					if chk_pri:
						c = chk_pri[0]

						if c.is_selected():
							print("[RPA] 'Generar para la actividad principal' ya estaba marcado (OK)")

						elif c.get_attribute("disabled") is not None:
							print("[RPA] 'Generar para la actividad principal' bloqueado por sistema (OK)")

						else:
							c.click()
							time.sleep(0.2)
							print("[RPA] Marcado por RPA: Generar para la actividad principal")
					else:
						print("[RPA] No se encontró checkbox en 'Generar para la actividad principal' (se omite)")
		

				# MOSTRAR FECHAS DE LA ACTIVIDAD
				if idx_fecha is not None and (idx_fecha + offset) < len(tds):
					celda_fecha = tds[idx_fecha + offset]
					chk_fecha = celda_fecha.find_elements(By.XPATH, ".//input[@type='checkbox' and contains(@name,'chkMosFec')]")
					if chk_fecha:
						c = chk_fecha[0]

						if c.is_selected():
							print("[RPA] 'Mostrar fechas de la actividad' ya estaba marcado (OK)")

						elif c.get_attribute("disabled") is not None:
							print("[RPA] 'Mostrar fechas de la actividad' bloqueado por sistema (OK)")

						else:
							c.click()
							time.sleep(0.2)
							print("[RPA] Marcado por RPA: Mostrar fechas de la actividad")

				procesadas += 1
				print("[RPA] Fila procesada correctamente")

			if procesadas == 0:
				print("[RPA][ERROR] No se procesaron filas habilitadas en certificación.")
				resultado.estado = 0
				resultado.error = 1
				resultado.continua = False
				resultado.mensaje_error = "No se procesaron filas habilitadas en certificación."
				return resultado

			# Grabar
			print("[RPA] Guardando configuración de certificación")
			wait.until(EC.element_to_be_clickable((
				By.XPATH,
				"//button[normalize-space(.)='Grabar' and contains(@onclick,'grabar')]"
			))).click()
			print("[RPA] Click en Grabar ejecutado")

			time.sleep(2)

			print("[RPA] Configuración completada")

			resultado.estado = 1
			resultado.error = 0
			resultado.continua = True
			resultado.mensaje_error = f"Config certificación OK. Filas procesadas: {procesadas}"
			return resultado

		except Exception as e:
			print("[RPA][ERROR] Fallo en configurarCertificacionDigitalCampusVirtual")
			print("[RPA][ERROR]", str(e))
			try:
				import traceback
				print(traceback.format_exc())
			except Exception:
				pass

			resultado.estado = 0
			resultado.error = 1
			resultado.continua = False
			resultado.mensaje_error = f"Error en configurarCertificacionDigitalCampusVirtual: {e}"
			return resultado

	def formatoCertificacionesCampusVirtual(self, url_get='', driver=''):

		resultado = ResultadoRPA()
		driver.get(self.url_ares)
		time.sleep(3)
		driver.get(url_get)
		time.sleep(4)
		try:

			wait = WebDriverWait(driver, 20)

			# Esperar la tabla de formatos
			wait.until(EC.presence_of_element_located((
				By.XPATH,
				"//div[contains(@class,'table-responsive')]//table//th[normalize-space()='Tipo de certificación']"
			)))

			crear_tipo = None
			
			print("[RPA] Proceso de Identificacion 1")

			for tipo in ["Diploma", "Certificado"]:

				xp_row = (
					"//table[contains(@class,'tblFormatos')]"
					f"//tr[td[2]//a[normalize-space()='{tipo}'] or td[2][normalize-space()='{tipo}']]"
				)

				
				if not driver.find_elements(By.XPATH, xp_row):
					continue

				# 1) ¿Ya confirmado? -> OK y salir
				confirmado = driver.find_elements(
					By.XPATH,
					xp_row + "//td//img[@title='Formato confirmado' or @alt='Formato confirmado']"
				)
				if confirmado:
					print(f"[RPA] {tipo}: Formato ya estaba CONFIRMADO (OK)")
					resultado.estado = 1
					resultado.error = 0
					resultado.continua = True
					resultado.mensaje_error = None
					return resultado

				# 2) ¿Existe formato NO confirmado? (tiene consultarFormato) -> confirmar y retornar
				links_consultar = driver.find_elements(
					By.XPATH,
					xp_row + "//td[2]//a[contains(@href,'consultarFormato')]"
				)
				if links_consultar:
					print(f"[RPA] {tipo}: Formato existe y NO está confirmado → Entrando a confirmar")
					driver.execute_script("arguments[0].click();", links_consultar[0])

					# Ya dentro del formato
					wait.until(EC.presence_of_element_located((
						By.XPATH, "//label[contains(normalize-space(.),'Configuración del encabezado')]"
					)))
					print("[RPA] Dentro del formato existente. Ejecutando confirmación...")

					# ===== CONFIRMAR FORMATO =====
					btn_confirmar = wait.until(EC.element_to_be_clickable((
						By.XPATH,
						"//button[normalize-space()='Confirmar' and contains(@onclick,'confirmar')]"
					)))
					btn_confirmar.click()
					print("[RPA] Click en botón Confirmar")

					wait.until(EC.presence_of_element_located((
						By.XPATH,
						"//label[contains(normalize-space(.),'Mensaje de confirmación')]"
					)))
					print("[RPA] Modal de confirmación visible")

					btn_aceptar = wait.until(EC.element_to_be_clickable((
						By.XPATH,
						"//div[contains(@class,'modal-footer')]"
						"//button[normalize-space()='Aceptar' and contains(@onclick,'submitOperacion')]"
					)))
					btn_aceptar.click()
					print("[RPA] Click en Aceptar (confirmación final)")

					wait.until(EC.presence_of_element_located((
						By.XPATH,
						"//span[contains(@class,'pucpCampoEstadoFinal') and normalize-space()='FORMATO CONFIRMADO']"
					)))
					print("[RPA] Formato confirmado (OK)")

					resultado.estado = 1
					resultado.error = 0
					resultado.continua = True
					resultado.mensaje_error = "Formato registrado existente confirmado (OK)."
					return resultado

				# 3) Si NO hay consultarFormato pero SÍ hay crearFormato -> se debe CREAR
				links_crear = driver.find_elements(
					By.XPATH,
					xp_row + "//a[contains(@href,'crearFormato')]"
				)
				if links_crear:
					crear_tipo = tipo
					print(f"[RPA] {tipo}: No existe formato → se debe CREAR")
					break

			# fuera del for
			if crear_tipo:
				print("[RPA] No hay formato pendiente de confirmación. Continúa a crear formato.")
			else:
				print("[RPA] No se encontró ni confirmar ni crear.")

			print("[RPA] Proceso de Identificacion 2")
			# según fila (Diploma primero, si no existe es Certificado)
			xp_lapiz_diploma = (
				"//table[contains(@class,'tblFormatos')]"
				"//tr[td[2]//a[normalize-space()='Diploma'] or td[2][normalize-space()='Diploma']]"
				"//a[contains(@href,'crearFormato')]"
			)
			xp_lapiz_certificado = (
				"//table[contains(@class,'tblFormatos')]"
				"//tr[td[2]//a[normalize-space()='Certificado'] or td[2][normalize-space()='Certificado']]"
				"//a[contains(@href,'crearFormato')]"
			)
			
			print("[RPA] Entrando a Generar nuevo Formato")
			try:
				wait.until(EC.element_to_be_clickable((By.XPATH, xp_lapiz_diploma))).click()
				es_diplomatura = True
			except TimeoutException:
				wait.until(EC.element_to_be_clickable((By.XPATH, xp_lapiz_certificado))).click()
				es_diplomatura = False

			print("[RPA] formatoCertificacionesCampusVirtual es_diplomatura =", es_diplomatura)
			time.sleep(5)
			
			# Asegurar pestaña Logos y encabezado
			tab_logos = wait.until(EC.element_to_be_clickable((
				By.XPATH, "//a[@data-toggle='tab' and @href='#divLogoEncabezado']"
			)))
			tab_logos.click()

			# Esperar que el panel esté activo
			wait.until(EC.presence_of_element_located((
				By.XPATH, "//div[@id='divLogoEncabezado' and contains(@class,'active')]"
			)))

			# Campo "Nombre(s) de la(s) unidad(es) que certifica(n)"
			campo_unidad = wait.until(EC.element_to_be_clickable((By.ID, "nombreUnidad")))
			campo_unidad.clear()
			campo_unidad.send_keys("CENTRUM PUCP")
			print("[RPA] Escribió nombre de la Unidad")

			print("[RPA] Inicia seleccion de firma")
			#Seleccion de Firma
			tab_firmas = wait.until(EC.element_to_be_clickable((
				By.XPATH, "//ul[@id='tabsFormato']//a[@href='#divFirmas']"
			)))
			driver.execute_script("arguments[0].click();", tab_firmas)
			print("[RPA] Selecciono de firma")
			
			wait.until(EC.presence_of_element_located((
				By.XPATH, "//ul[@id='tabsFormato']//li[contains(@class,'active')]//a[@href='#divFirmas']"
			)))
			print("[RPA] confirmacion de firma")

			# esperar que el formulario de firma 1 ya esté listo
			wait.until(EC.element_to_be_clickable((By.ID, "comboUnidadFirma1")))
			print("[RPA] espera de formulario de firmas")

			# ===== FIRMA 1 =====
			print("[RPA] Inicio de proceso de Firma 1")
			
			Select(wait.until(EC.element_to_be_clickable((By.ID, "comboUnidadFirma1")))) \
            .select_by_value("64181")
			print("[RPA] selecciono unidad")
			
			wait.until(lambda d: len(
				Select(d.find_element(By.ID, "comboCargoBancoFirmas1")).options
			) > 1)
			print("[RPA] espera")
			
			Select(wait.until(EC.element_to_be_clickable(
				(By.ID, "comboCargoBancoFirmas1"))
			)).select_by_value("19;64181")
			print("[RPA] selecciono cargo")
			
			wait.until(lambda d: len(
				Select(d.find_element(By.ID, "comboDenominacionCargo1")).options
			) > 1)
			print("[RPA] espera")
			
			Select(wait.until(EC.element_to_be_clickable((By.ID, "comboDenominacionCargo1")))) \
    			.select_by_value("2")
			print("[RPA] selecciono denominacion")
			print("[RPA] Proceso de Firma 1 Completado")

			# ===== FIRMA 2 =====
			print("[RPA] Inicio de proceso de Firma 2")
			
			Select(wait.until(EC.element_to_be_clickable((By.ID, "comboUnidadFirma2")))) \
            	.select_by_value("64181")
			print("[RPA] selecciono unidad")
			
			wait.until(lambda d: len(
				Select(d.find_element(By.ID, "comboCargoBancoFirmas2")).options
			) > 1)
			print("[RPA] espera")
			
			Select(wait.until(EC.element_to_be_clickable(
				(By.ID, "comboCargoBancoFirmas2"))
			)).select_by_value("10;64181")
			print("[RPA] selecciono cargo")

			wait.until(lambda d: len(
				Select(d.find_element(By.ID, "comboPersonaFirmas2")).options
			) > 1)
			print("[RPA] espera")

			select_persona = Select(wait.until(
				EC.element_to_be_clickable((By.ID, "comboPersonaFirmas2"))
			))

			
			valor_actual = select_persona.first_selected_option.get_attribute("value")

			if not valor_actual:
				select_persona.select_by_value(self.cer_segundo)
				print("[RPA] Firma 2: persona no preseleccionada, se selecciona AMADOR")
			else:
				
				print("[RPA] Firma 2: persona ya preseleccionada")
			
			wait.until(lambda d: len(
				Select(d.find_element(By.ID, "comboDenominacionCargo2")).options
			) > 1)
			print("[RPA] espera")
			
			Select(wait.until(EC.element_to_be_clickable((By.ID, "comboDenominacionCargo2")))) \
            	.select_by_value("2")
			print("[RPA] selecciono unidad")
			print("[RPA] Proceso de Firma 2 Completado")

			
			wait.until(EC.element_to_be_clickable((
				By.XPATH, "//button[normalize-space()='Grabar' and contains(@onclick,'grabar')]"
			))).click()
			print("[RPA] grabo")
			
			wait.until(EC.presence_of_element_located((
				By.XPATH, "//label[contains(normalize-space(.),'Confirmación de actualización')]"
			)))
			print("[RPA] espera popup")
			
			wait.until(EC.element_to_be_clickable((
				By.XPATH, "//button[normalize-space()='Continuar y grabar' and contains(@onclick,'finalizarRegistro')]"
			))).click()
			print("[RPA] continuo y grabo")
			
			#Regresa
			wait.until(EC.presence_of_element_located((
				By.XPATH, "//label[contains(normalize-space(.),'Configuración del encabezado')]"
			)))

			time.sleep(5)

			# ===== CONFIRMAR FORMATO =====

			# Clic en botón "Confirmar"
			btn_confirmar = wait.until(EC.element_to_be_clickable((
				By.XPATH,
				"//button[normalize-space()='Confirmar' and contains(@onclick,'confirmar')]"
			)))
			btn_confirmar.click()
			print("[RPA] Click en botón Confirmar")

			# ===== POPUP DE CONFIRMACIÓN =====

			# Esperar que aparezca el modal
			wait.until(EC.presence_of_element_located((
				By.XPATH,
				"//label[contains(normalize-space(.),'Mensaje de confirmación')]"
			)))
			print("[RPA] Modal de confirmación visible")

			# Clic en botón "Aceptar" del modal
			btn_aceptar = wait.until(EC.element_to_be_clickable((
				By.XPATH,
				"//div[contains(@class,'modal-footer')]"
				"//button[normalize-space()='Aceptar' and contains(@onclick,'submitOperacion')]"
			)))
			btn_aceptar.click()
			print("[RPA] Click en Aceptar (confirmación final)")

			# Esperar confirmación en la página
			wait.until(EC.presence_of_element_located((
				By.XPATH,
				"//span[contains(@class,'pucpCampoEstadoFinal') and normalize-space()='FORMATO CONFIRMADO']"
			)))

			print("[RPA] Formato confirmado y proceso finalizado")

			# OK
			resultado.estado = 1
			resultado.error = 0
			resultado.continua = True
			resultado.mensaje_error = f"Formato de certificación OK (grabado y confirmado)."
			return resultado

		except Exception as e:
			resultado.estado = 0
			resultado.error = 1
			resultado.continua = False
			resultado.mensaje_error = f"Error en formatoCertificacionesCampusVirtual: {str(e)}"
			return resultado	
		
	def DocentesValidacion(self, url_get='', driver='', data_docente_map=None, norm_fn=None, nombre_programa=""):

		resultado = ResultadoRPA()
		driver.get(self.url_eros)
		time.sleep(3)
		driver.get(url_get)
		time.sleep(4)

		try:
			print("[RPA] Iniciando DocentesValidacion")

			wait = WebDriverWait(driver, 15)

			# Ancla de pantalla
			wait.until(EC.presence_of_element_located((
				By.XPATH, "//*[contains(normalize-space(.),'Docentes de la actividad')]"
			)))
			print("[RPA] Pantalla 'Docentes de la actividad' detectada")

			# Estados OK = no tocar
			estados_ok = {"ACEPTADO", "CONTRATADO", "EN CONTRATACIÓN", "EN CONTRATACION"}

			cursos_ok = 0
			cursos_en_eval = 0
			errores = []

			links_ir = driver.find_elements(
				By.XPATH,
				"//a[contains(normalize-space(.),'Ir a la actividad') and contains(@href,'accion=BuscarListaDocentes')]"
			)
			
			# detectar layout
			modo_curso_unico = (len(links_ir) == 0)

			# normalizar iteración
			total = 1 if modo_curso_unico else len(links_ir)
			print(f"[RPA] Cursos detectados: {total} (curso_unico={modo_curso_unico})")

			for i in range(total):
				print(f"\n[RPA] -------------------------------")
				print(f"[RPA] Procesando bloque #{i+1}")

				if not modo_curso_unico:
				# Asegurar pantalla lista
					if "accion=BuscarListaDocentes" not in driver.current_url:
						driver.get(url_get)
						time.sleep(2)

					wait.until(EC.presence_of_element_located((
						By.XPATH, "//*[contains(normalize-space(.),'Docentes de la actividad')]"
					)))

					# volver a traer la lista
					links_ir = driver.find_elements(
						By.XPATH,
						"//a[contains(normalize-space(.),'Ir a la actividad') and contains(@href,'accion=BuscarListaDocentes')]"
					)

					# tomar el i-ésimo link real
					link_ir = links_ir[i]

					# bloque y título correctos para link
					bloque = link_ir.find_element(By.XPATH, "ancestor::table[contains(@class,'pucpTablaSubTitulo')][1]")

					# Log del título
					titulo = ""
					try:
						titulo = bloque.find_element(By.XPATH, ".//td[contains(@class,'pucpSubTitulo')][1]").text.strip()
						if titulo:
							print("[RPA] Curso:", titulo)
					except Exception:
						titulo = ""
				
				else:
					# título viene del encabezado superior
					bloque = None
					try:
						titulo = driver.find_element(By.XPATH, "//td[contains(@class,'pucpTitulo')]").text.strip()
						print("[RPA] Curso único:", titulo)
					except Exception:
						msg = "No se pudo leer el título del curso único (td.pucpTitulo)."
						print("[RPA][ERROR]", msg)
						errores.append(msg)
						continue

				#Normalizar con la función
				if norm_fn:
					titulo_norm = norm_fn(titulo)
				else:
					titulo_norm = titulo.strip().lower()


				data_docente = (data_docente_map or {}).get(titulo_norm)

				# procesar cursos que vienen en det_prog
				if data_docente_map and (titulo_norm not in data_docente_map):
					print(f"[RPA] (skip) Curso fuera de det_prog: {titulo}")
					continue

				# si el curso está dentro del mapa pero no hay data_docente válida
				if not data_docente:
					msg = f"Bloque #{i+1}: no se encontró data_docente (BD) para el curso: '{titulo}'."
					print("[RPA][ERROR]", msg)
					errores.append(msg)
					continue

				cod_bd = str(data_docente.get("cod_docente", "")).strip()
				if not cod_bd:
					msg = f"Bloque #{i+1}: data_docente.cod_docente vacío para el curso: '{titulo}'."
					print("[RPA][ERROR]", msg)
					errores.append(msg)
					continue

				# 1) la tabla de datos viene inmediatamente después del bloque
				if modo_curso_unico:
					tabla_datos = driver.find_element(
						By.XPATH, "//table[.//input[@name='estadoDocente']]")
				else:
					try:
						tabla_datos = driver.find_element(By.XPATH,
							"(//table[contains(@class,'pucpTablaSubTitulo')][.//a[contains(normalize-space(.),'Ir a la actividad')]])[{idx}]"
							"/following-sibling::table[1][.//input[@name='estadoDocente'] or .//a[contains(@href,'AbrirInscDocente')] or .//td[contains(@class,'pucpLinkCelda')]]"
							.format(idx=i+1)
						)
					except Exception:
						tabla_datos = None

				# 2) Fallback: buscar la primera tabla válida DESPUÉS del bloque pero ANTES del siguiente bloque
				if not modo_curso_unico and not tabla_datos:
					try:
						tabla_datos = driver.find_element(By.XPATH,
							"(//table[contains(@class,'pucpTablaSubTitulo')][.//a[contains(normalize-space(.),'Ir a la actividad')]])[{idx}]"
							"/following::table"
							"[.//input[@name='estadoDocente'] or .//a[contains(@href,'AbrirInscDocente')] or .//td[contains(@class,'pucpLinkCelda')]]"
							"[count(. | (//table[contains(@class,'pucpTablaSubTitulo')][.//a[contains(normalize-space(.),'Ir a la actividad')]])[{idx}]/following::table[contains(@class,'pucpTablaSubTitulo')][1]/preceding::table) "
							" = count((//table[contains(@class,'pucpTablaSubTitulo')][.//a[contains(normalize-space(.),'Ir a la actividad')]])[{idx}]/following::table[contains(@class,'pucpTablaSubTitulo')][1]/preceding::table)]"
							"[1]"
							.format(idx=i+1)
						)
					except Exception:
						tabla_datos = None

				# DETERMINAR SI EL CURSO NO TIENE DOCENTES
				filas_reales = []
				if tabla_datos:
					filas_reales = tabla_datos.find_elements(
						By.XPATH,
						".//tr[.//input[@name='estadoDocente'] or .//a[contains(@href,'AbrirInscDocente')]]"
					)

				sin_docentes = (not tabla_datos) or (len(filas_reales) == 0)

				fila_docente_bd = None

				if filas_reales and cod_bd:
					for f in filas_reales:
						try:
							cod_tabla = f.find_element(By.XPATH,".//input[@type='hidden' and @name='codigo']").get_attribute("value").strip()
						except Exception:
							cod_tabla = ""

						if cod_tabla == cod_bd:
							fila_docente_bd = f
							break

				# hay filas, pero no está el docente que exige BD
				if filas_reales and not fila_docente_bd:
					print(f"[RPA] Docente {cod_bd} no existe en el curso → flujo sin_docentes")
					sin_docentes = True

				# flujo sin docentes 
				if sin_docentes:
						print("[RPA] Sin docentes detectado (se procederá a añadir)")

						try:
							# obtener data_docente desde el mapa por título del curso
							if not data_docente_map:
								msg = f"Bloque #{i+1}: sin docentes y no se proporcionó data_docente_map."
								print("[RPA][ERROR]", msg)
								errores.append(msg)
								continue

							if not data_docente:
								msg = f"Bloque #{i+1}: sin docentes y no se encontró data BD para el curso: '{titulo}'."
								print("[RPA][ERROR]", msg)
								errores.append(msg)
								continue

							if not modo_curso_unico:
								# 1) Click en "Ir a la actividad" (del bloque actual)
								btn_ir = bloque.find_elements(By.XPATH,
									".//a[contains(normalize-space(.),'Ir a la actividad') and contains(@href,'accion=BuscarListaDocentes')]"
								)
								if not btn_ir:
									msg = f"Bloque #{i+1}: no se encontró link 'Ir a la actividad'."
									print("[RPA][ERROR]", msg)
									errores.append(msg)
									continue

								driver.execute_script("arguments[0].click();", btn_ir[0])
								print("[RPA] Click en 'Ir a la actividad'")
							else:
								
								# Curso único: ya estamos dentro de la actividad
								print("[RPA] Curso único: no se requiere 'Ir a la actividad'")

							# 2) Click "Añadir" (CrearInscDocente)
							btn_add = wait.until(EC.element_to_be_clickable((
								By.XPATH,
								"//button[(normalize-space(.)='Añadir' or normalize-space(.)='Anadir') and contains(@onclick,'accion=CrearInscDocente')]"
							)))
							driver.execute_script("arguments[0].click();", btn_add)
							print("[RPA] Click en 'Añadir'")

							# 3) Esperar formulario
							wait.until(EC.presence_of_element_located((
								By.XPATH, "//*[contains(normalize-space(.),'Información del Docente')]"
							)))
							print("[RPA] Formulario 'Información del Docente' abierto")

							# 4) Llenar formulario
							cod_docente = str(data_docente.get("cod_docente", "")).strip()
							ini_labor   = data_docente.get("ini_labor")        
							fin_labor   = data_docente.get("fin_labor")        
							rol_text    = str(data_docente.get("rol_text", "")).strip()
							horas_ded   = str(data_docente.get("horas_dedicacion", "")).strip()

							if not cod_docente:
								raise Exception("data_docente.cod_docente vacío")

							inp_cod = wait.until(EC.element_to_be_clickable((By.ID, "codigoBusqueda")))
							inp_cod.clear()
							inp_cod.send_keys(cod_docente)
							
							# blur + click fuera
							driver.execute_script("arguments[0].blur();", inp_cod)
							driver.execute_script("document.body.click();")

							wait.until(lambda d: d.find_element(By.NAME, "nombres").get_attribute("value").strip() != "")

							# Inicio labor
							if ini_labor:
								Select(driver.find_element(By.NAME, "diaFecIni")).select_by_value(f"{ini_labor.day:02d}")
								Select(driver.find_element(By.NAME, "mesFecIni")).select_by_value(f"{ini_labor.month:02d}")
								Select(driver.find_element(By.NAME, "anhoFecIni")).select_by_value(str(ini_labor.year))

							# Fin labor
							if fin_labor:
								Select(driver.find_element(By.NAME, "diaFecFin")).select_by_value(f"{fin_labor.day:02d}")
								Select(driver.find_element(By.NAME, "mesFecFin")).select_by_value(f"{fin_labor.month:02d}")
								Select(driver.find_element(By.NAME, "anhoFecFin")).select_by_value(str(fin_labor.year))

							# Rol
							if rol_text:
								sel_rol = Select(driver.find_element(By.ID, "comboRolDocente"))  

								# match exacto
								sel_rol.select_by_visible_text(rol_text)

							if horas_ded:
								inp_horas = driver.find_element(By.NAME, "horas")
								inp_horas.clear()
								inp_horas.send_keys(horas_ded)

							# 5) Grabar
							btn_grabar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(.)='Grabar']")))
							btn_grabar.click()
							print("[RPA] Click en 'Grabar'")

							time.sleep(2)

							# 6) Solicitar aprobación INMEDIATAMENTE
							try:
								# A veces el botón aparece en la misma pantalla, a veces en el detalle; probamos directo
								btn_solicitar = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((
									By.XPATH, "//button[normalize-space(.)='Solicitar Aprobación' or normalize-space(.)='Solicitar Aprobacion']"
								)))
								driver.execute_script("arguments[0].click();", btn_solicitar)
								print("[RPA] Click en 'Solicitar Aprobación' (post-grabar)")

								# Esperar un poco para que procese
								time.sleep(2)

							except Exception:
								print("[RPA][WARN] No se encontró/activó 'Solicitar Aprobación' post-grabar.")

							# 7) Volver al listado por link del programa
							link_programa = wait.until(EC.element_to_be_clickable((
								By.XPATH,
								"//a[contains(@href,'accion=BuscarListaDocentes') and contains(@href,'tipoProceso=') and contains(@href,'identificaProceso=')]"
							)))
							driver.execute_script("arguments[0].click();", link_programa)
							print("[RPA] Volviendo por link del programa (BuscarListaDocentes)")

							wait.until(EC.presence_of_element_located((
								By.XPATH, "//*[contains(normalize-space(.),'Docentes de la actividad')]"
							)))
							print("[RPA] De vuelta a 'Docentes de la actividad'")

							cursos_en_eval += 1
							continue

						except Exception as e:
							msg = f"Bloque #{i+1}: error al añadir docente: {e}"
							print("[RPA][ERROR]", msg)
							errores.append(msg)
							continue
						
				print(f"[RPA] Curso con docentes detectados: (cod={cod_bd})")

				# VALIDACIÓN DE FECHAS
				try:
					if not sin_docentes and data_docente and fila_docente_bd:
						
						bd_ini = data_docente.get("ini_labor")
						bd_fin = data_docente.get("fin_labor")

						if bd_ini and bd_fin and filas_reales:

							tab_ini, tab_fin = self._leer_fechas_tabla_docente(fila_docente_bd)

							print(f"[RPA] Fechas tabla: {tab_ini} - {tab_fin} | BD: {bd_ini} - {bd_fin}")

							if tab_ini is None or tab_fin is None:
								print("[RPA][WARN] No se pudieron leer fechas de la tabla")
							elif (tab_ini != bd_ini) or (tab_fin != bd_fin):

								print("[RPA] Fechas NO coinciden en tabla con BD")

								self.enviarCorreoFechasDistintasValidacionDocentes(
									nombre_programa=nombre_programa,
									titulo_curso=titulo,
									tab_ini=tab_ini,
									tab_fin=tab_fin,
									bd_ini=bd_ini,
									bd_fin=bd_fin
								)

								errores.append(
									f"Bloque #{i+1}: Inconsistencia de fechas de labor detectada.\n"
									f"Programa: {nombre_programa}.\n"
									f"Curso: {titulo}.\n"
									f"Campus Virtual → Inicio de labor: {tab_ini}, Fin de labor: {tab_fin}.\n"
									f"Último horario registrado (CISAM) → Inicio de labor: {bd_ini}, Fin de labor: {bd_fin}."
								)
								continue

					elif not data_docente:
						print("[RPA][WARN] No hay data_docente para validar fechas")

				except Exception as e:
					msg = f"Bloque #{i+1}: error al validar fechas: {e}"
					print("[RPA][ERROR]", msg)
					errores.append(msg)
					continue

				if not fila_docente_bd:
					print(f"[RPA] No existe fila del docente {cod_bd} -> se considera sin_docentes")
					cursos_en_eval += 1
					continue

				# LEER ESTADO SOLO DE LA FILA DEL DOCENTE
				estado_docente = ""
				td_estado_list = fila_docente_bd.find_elements(
					By.XPATH,
					".//td[.//input[@type='hidden' and @name='estadoDocente']]"
				)

				if td_estado_list:
					celda_estado = td_estado_list[0]
					divs = celda_estado.find_elements(By.XPATH, ".//div")
					if divs and divs[0].text.strip():
						estado_docente = divs[0].text.strip().upper()
					else:
						estado_docente = celda_estado.text.strip().upper()

				print(f"[RPA] Estado: {estado_docente}")

				if not estado_docente:
					msg = f"Bloque #{i+1}: no se pudo leer el estado."
					print("[RPA][ERROR]", msg)
					errores.append(msg)
					continue

				# 1) RETIRADO -> se considera sin docentes vigentes
				if estado_docente == "RETIRADO":
					cursos_en_eval += 1
					print("[RPA] Docente RETIRADO -> se considera sin docentes vigentes (pendiente)")
					continue

				# 2) REGISTRADO -> entrar al detalle y solicitar aprobación
				if estado_docente == "REGISTRADO":
					print("[RPA] Caso REGISTRADO: solicitando aprobación")
					try:
						link_docente = fila_docente_bd.find_element(
							By.XPATH,
							".//td[contains(@class,'pucpLinkCelda')]//a[contains(@href,'AbrirInscDocente')]"
						)
						driver.execute_script("arguments[0].click();", link_docente)

						wait.until(EC.presence_of_element_located((
							By.XPATH, "//*[contains(normalize-space(.),'Información del Docente')]"
						)))
						print("[RPA] Dentro del detalle del docente")

						btn_solicitar = wait.until(EC.element_to_be_clickable((
							By.XPATH,
							"//button[normalize-space(.)='Solicitar Aprobación' or normalize-space(.)='Solicitar Aprobacion']"
						)))
						driver.execute_script("arguments[0].click();", btn_solicitar)
						print("[RPA] Click en 'Solicitar Aprobación'")

						# Volver al listado por link del programa
						link_programa = wait.until(EC.element_to_be_clickable((
							By.XPATH,
							"//a[contains(@href,'accion=BuscarListaDocentes') and contains(@href,'tipoProceso=') and contains(@href,'identificaProceso=')]"
						)))
						driver.execute_script("arguments[0].click();", link_programa)

						wait.until(EC.presence_of_element_located((
							By.XPATH, "//*[contains(normalize-space(.),'Docentes de la actividad')]"
						)))
						print("[RPA] De vuelta a 'Docentes de la actividad'")

						cursos_en_eval += 1
						continue

					except Exception as e:
						msg = f"Bloque #{i+1}: error en REGISTRADO (docente {cod_bd}) al entrar/solicitar: {e}"
						print("[RPA][ERROR]", msg)
						errores.append(msg)
						continue

				# 3) EN EVALUACIÓN -> no se toca
				if estado_docente in ("EN EVALUACIÓN", "EN EVALUACION"):
					cursos_en_eval += 1
					print("[RPA] Docente en EN EVALUACIÓN (no se toca)")
					continue

				# 4) Estados OK -> curso OK
				if estado_docente in estados_ok:
					cursos_ok += 1
					print("[RPA] Docente OK")
					continue

				# 5) Otros -> error
				msg = f"Bloque #{i+1}: estado docente no contemplado (docente {cod_bd}): {estado_docente}"
				print("[RPA][ERROR]", msg)
				errores.append(msg)
				continue

			# Resultado global
			if errores:
				resultado.estado = 0
				resultado.error = 1
				resultado.continua = False
				resultado.mensaje_error = " | ".join(errores)
				return resultado

			if cursos_en_eval > 0:
				resultado.estado = 0
				resultado.error = 0
				resultado.continua = True
				resultado.mensaje_error = f"Hay cursos EN EVALUACIÓN/pendientes: {cursos_en_eval}. OK: {cursos_ok}."
				return resultado

			resultado.estado = 1
			resultado.error = 0
			resultado.continua = True
			resultado.mensaje_error = None
			return resultado

		except Exception as e:
			print("[RPA][ERROR] Fallo en DocentesValidacion")
			print("[RPA][ERROR]", str(e))
			try:
				import traceback
				print(traceback.format_exc())
			except Exception:
				pass

			resultado.estado = 0
			resultado.error = 1
			resultado.continua = False
			resultado.mensaje_error = f"Error en DocentesValidacion: {e}"
			return resultado
		
	
	def enviarCorreoFechasDistintasValidacionDocentes(self,nombre_programa,titulo_curso,tab_ini,tab_fin,bd_ini,bd_fin):

		try:
			#emails = [self.email]
			emails = [e.strip() for e in self.emails_pago.split(",")]
			cc = []
			bcc = [self.bcc]

			subject = f"Importante: Fechas de labor distintas en Docentes - {nombre_programa} "
			from_address = "Plataforma-Centrum <noreply@centrummailing.pucp.edu.pe>"

			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)
			if cc:
				msg['Cc'] = ", ".join(cc)
			msg['Subject'] = subject

			# Formatear fechas
			def _fmt(d):
				try:
					return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else (str(d) if d is not None else "-")
				except Exception:
					return str(d)

			tab_ini_s = _fmt(tab_ini)
			tab_fin_s = _fmt(tab_fin)
			bd_ini_s  = _fmt(bd_ini)
			bd_fin_s  = _fmt(bd_fin)

			html = f"""
			<!DOCTYPE html>
			<html>
			<head>
				<meta charset="utf-8">
				<title>Fechas de labor distintas</title>
			</head>
			<body>
			<table align="center" width="100%" cellpadding="0" cellspacing="0"
				style="background-color:#ffffff;font-family:Helvetica,Arial,sans-serif;">
				<tr>
				<td align="center">

					<table width="100%" cellpadding="0" cellspacing="0"
					style="background-image:url('https://centrumwebs.pucp.edu.pe/cisam/public/img/modulo/header_image.jpg');
					background-size:cover;background-position:center;padding:20px 0;">
					<tr>
						<td align="center">
						<img src="https://centrumwebs.pucp.edu.pe/cisam/public/img/login/logo-blanco.png"
							width="220" height="68" alt="CENTRUM PUCP"
							style="display:block;border:0;">
						</td>
					</tr>
					</table>

					<table width="600" cellpadding="0" cellspacing="0"
					style="background:#ffffff;margin-top:20px;border-collapse:collapse;">

					<tr>
						<td style="padding:20px;color:#174275;font-size:18px;">
						<strong>Validación de Docentes – Fechas de labor distintas</strong>
						</td>
					</tr>

					<tr>
						<td style="padding:0 20px 10px;color:#174275;font-size:15px;">
						<p>Estimados,</p>

						<p>
							Durante la <strong>Validación de Docentes</strong> se detectó una
							inconsistencia entre las fechas de labor registradas en
							<strong>Campus Virtual</strong> y las fechas definidas en el
							<strong>último horario registrado</strong>.
						</p>

						<div style="background:#f4f8fc;border:1px solid #d9e6f2;
							border-radius:6px;padding:12px;margin:10px 0;">
							<div><strong>Programa:</strong> {nombre_programa}</div>
							<div><strong>Curso:</strong> {titulo_curso}</div>
						</div>
						</td>
					</tr>

					<tr>
						<td style="padding:0 20px 20px;">
						<table width="100%" cellpadding="0" cellspacing="0"
							style="border:1px solid #d9e6f2;border-radius:6px;
							border-collapse:separate;overflow:hidden;">
							<tr style="background:#174275;color:#ffffff;">
							<th align="left" style="padding:10px;">Origen</th>
							<th align="left" style="padding:10px;">Inicio labor</th>
							<th align="left" style="padding:10px;">Fin labor</th>
							</tr>
							<tr>
							<td style="padding:10px;">Campus Virtual</td>
							<td style="padding:10px;">{tab_ini_s}</td>
							<td style="padding:10px;">{tab_fin_s}</td>
							</tr>
							<tr>
							<td style="padding:10px;">Último horario registrado</td>
							<td style="padding:10px;">{bd_ini_s}</td>
							<td style="padding:10px;">{bd_fin_s}</td>
							</tr>
						</table>
						</td>
					</tr>

					<tr>
						<td style="padding:0 20px 20px;color:#174275;font-size:14px;">
						<p>
							Por favor, corregir las fechas para que coincidan y volver a ejecutar el RPA.
						</p>
						<p style="color:#6b7a90;font-size:12px;">
							Mensaje generado automáticamente por el RPA – Validación de Docentes.
						</p>
						</td>
					</tr>

					</table>

				</td>
				</tr>
			</table>
			</body>
			</html>
			"""

			msg.attach(MIMEText(html, 'html'))

			msg_string = msg.as_string()
			toaddrs = emails + cc + bcc

			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			print(from_address, toaddrs)
			server.sendmail(from_address, toaddrs, msg_string)
			server.quit()

			print(f"[RPA][MAIL] Correo enviado por fechas distintas: {nombre_programa} | {titulo_curso}")

		except Exception as e:
			print(f"[RPA][WARN] No se pudo enviar correo de fechas distintas ({nombre_programa} | {titulo_curso}): {e}")
	
	def _parse_fecha_campus(self, txt):

		if not txt:
			return None

		txt = str(txt).strip()

		# Normalizar separadores
		txt = txt.replace("/", "-")

		meses = {
			"ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
			"JUL": 7, "AGO": 8, "SEP": 9, "SET": 9,
			"OCT": 10, "NOV": 11, "DIC": 12
		}

		
		m = re.search(r"(\d{1,2})-([A-Za-zñÑ]{3})-(\d{2,4})", txt)
		if not m:
			return None

		d = int(m.group(1))
		mon = m.group(2).upper()
		y = int(m.group(3))

		
		if y < 100:
			y += 2000

		if mon not in meses:
			return None

		try:
			return datetime(y, meses[mon], d).date()
		except Exception:
			return None
		
	def _leer_fechas_tabla_docente(self, fila):
		try:
			tds = fila.find_elements(By.XPATH, "./td")

			if len(tds) < 6:
				return None, None

			ini_txt = tds[4].text.strip()  
			fin_txt = tds[5].text.strip()  

			ini = self._parse_fecha_campus(ini_txt)
			fin = self._parse_fecha_campus(fin_txt)

			return ini, fin

		except Exception:
			return None, None
	
	def closeCampusVirtual(self, driver=''):
		driver.close()

	def logInCampusVirtualPagos(self, driver=''):
		driver.get(f"{self.url_pandora}/pucp/login")
		wait = WebDriverWait(driver, 10)


		usuario = self.user_pago
		password = self.pass_pago
		
		username_input =  WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
		)
		username_input.send_keys(usuario)
		password_input =  WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
		)
		password_input.send_keys(password)
		submit_login_button = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@class='submit izq']"))
		)
		
		submit_login_button.click()

		try:
			wait.until(
				lambda d:
					d.find_elements(By.XPATH, "//div[contains(@class,'cierre-correcto')]") 
			)
		except TimeoutException:
			#emails = 'abarbozab@pucp.pe'
			#Colocar correo de manuel tambien
			emails = [self.email]
			cc = [] 
			bcc = [self.bcc]

			subject = 'FALLO VALIDACIÓN INICIO DE SESIÓN RPA SISTEMA DE EVALUACIÓN NO GRADO FUNCION PAGOS'
			from_address = "Plataforma-Centrum <noreply@centrummailing.pucp.edu.pe>"

			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)       

			if cc:
				msg['Cc'] = ", ".join(cc)      

			msg['Subject'] = subject
			text_email_student = f"""
							<html>
							<body>
								<p>Estimados,</p>
								<p>El RPA de creación de sistema de evaluación no pudo iniciar sesión en el Campus Virtual.</p>
							</body>
							</html>
							"""     
			msg.attach(MIMEText(text_email_student, 'html'))

			msg_string = msg.as_string()

			toaddrs = emails + cc + bcc         

			
			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			#text = msg.as_string()
			server.sendmail(from_address, toaddrs, msg_string)
			server.quit()
			print("No se pudo validar el login: no se encontró ni 'cierre-correcto', "
				"ni 'tabParticipando', ni el formulario de login.")
			'''
			raise RuntimeError(
				"No se pudo validar el login: no se encontró ni 'cierre-correcto', "
				"ni 'tabParticipando', ni el formulario de login."
			)
			'''

		if driver.find_elements(By.XPATH, "//div[contains(@class,'cierre-correcto')]"):
			print("[RPA] Login correcto (pantalla 'Inicio de sesión correcto').")
			return driver

		print("Estado de login indeterminado tras enviar el formulario.")
		#raise RuntimeError("Estado de login indeterminado tras enviar el formulario.")
	

	def escribirInput(self, elemento, valor):
		valor_str = "" if valor is None else str(valor)

		try:
			elemento.click()
		except Exception:
			pass

		try:
			elemento.send_keys(Keys.CONTROL, "a")
			elemento.send_keys(Keys.DELETE)
		except Exception:
			try:
				elemento.clear()
			except Exception:
				pass

		elemento.send_keys(valor_str)

		# Validar contra el valor del input 
		valor_input = (elemento.get_attribute("value") or "").strip()
		if valor_input == valor_str.strip():
			return True

		# Intentar validar contra el texto visible en pantalla
		texto_visible = (elemento.text or "").strip()
		if valor_str.strip() in texto_visible:
			return True

		raise Exception("No se pudo validar el texto ingresado en el elemento.")
	
	def escribirInput2(self, elemento, valor):
		valor_str = "" if valor is None else str(valor)
		print(valor_str)
		try:
			elemento.click()
		except:
			pass

		try:
			elemento.send_keys(Keys.CONTROL, "a")
			elemento.send_keys(Keys.DELETE)
		except:
			try:
				elemento.clear()
			except:
				pass

		elemento.send_keys(valor_str)

		# MUY IMPORTANTE para ProForma
		elemento.send_keys(Keys.ENTER)

		# Pequeña espera para que React procese el cambio
		time.sleep(1)
		
		valor_input = (elemento.get_attribute("value") or "").strip()
		print(valor_input)
		'''
		if valor_input == valor_str.strip():
			return True

		raise Exception(
			f"No se pudo validar el texto ingresado. "
			f"Esperado='{valor_str}' Obtenido='{valor_input}'"
		)
		'''

	def buscarElemento(self, wait, descripciones_xpath):

		error = None
		for descriptor in descripciones_xpath:
			try:
				if isinstance(descriptor, (tuple, list)) and len(descriptor) == 2:
					by, selector = descriptor[0], descriptor[1]
				else:
					by, selector = By.XPATH, descriptor

				try:
					elemento = wait.until(EC.element_to_be_clickable((by, selector)))
					return elemento, "{}={}".format(by, selector)
				except Exception:
					pass

				try:
					elemento = wait.until(EC.visibility_of_element_located((by, selector)))
					return elemento, "{}={}".format(by, selector)
				except Exception:
					pass

				elemento = wait.until(EC.presence_of_element_located((by, selector)))
				return elemento, "{}={}".format(by, selector)
			except Exception as e:
				error = e
				continue

		raise error if error is not None else Exception("No se pudo ubicar elemento con fallbacks.")

	def setCheckbox(self, driver, wait, etiqueta_log, lista_xpath, marcado=True):
		def obtener_estado_checkbox(elemento):
			try:
				return bool(elemento.is_selected())
			except Exception:
				pass

			try:
				aria = (elemento.get_attribute("aria-checked") or "").strip().lower()
				if aria in ("true", "false"):
					return aria == "true"
			except Exception:
				pass

			try:
				checked_attr = elemento.get_attribute("checked")
				if checked_attr is not None:
					return str(checked_attr).lower() in ("true", "checked", "1")
			except Exception:
				pass

			return False

		checkbox, xpath_usado = self.buscarElemento(
			wait=wait,
			descripciones_xpath=lista_xpath,
		)

		driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkbox)
		estado_actual = obtener_estado_checkbox(checkbox)

		if estado_actual != bool(marcado):
			try:
				checkbox.click()
			except Exception:
				driver.execute_script("arguments[0].click();", checkbox)
			time.sleep(0.4)

		estado_final = obtener_estado_checkbox(checkbox)
		if estado_final != bool(marcado):
			raise Exception(f"No se pudo cambiar estado de checkbox {etiqueta_log}.")

		print(f"[RPA][CAMBIO_FECHA] Checkbox '{etiqueta_log}' OK usando {xpath_usado}. Marcado={estado_final}")
		return True

	def cambiarFechasActividad(
		self,
		driver="",
		programa="",
		fecha_inicio_dice="",
		fecha_inicio_debe_decir="",
		fecha_fin_dice="",
		fecha_fin_debe_decir="",
		 fecha_correo_ini_dice="",
		fecha_correo_fin_dice="",
		fecha_correo_ini_debe="",
		fecha_correo_fin_debe=""
	):
		resultado = ResultadoRPA()
		nombre_unidad = "DARSA"
		compartir_con = "Nadie"
		motivo_solicitud = "Se requiere para correcta emisión"
		url_portal = "https://ti-dec-pucp.atlassian.net/servicedesk/customer/portals"

		campos_enviados = {
			"nombre_unidad": nombre_unidad,
			"programa": programa,
			"compartir_con": compartir_con,
			"fecha_inicio_dice": fecha_inicio_dice,
			"fecha_inicio_debe_decir": fecha_inicio_debe_decir,
			"fecha_fin_dice": fecha_fin_dice,
			"fecha_fin_debe_decir": fecha_fin_debe_decir,
			"motivo_solicitud": motivo_solicitud
		}

		def compartir_con_seleccionado():
			valores_directos = driver.find_elements(By.CSS_SELECTOR, "#react-select-2-single-value")
			if valores_directos:
				return (valores_directos[0].text or "").strip() == compartir_con

			input_compartir = driver.find_elements(By.CSS_SELECTOR, "#customfield_10002")
			if not input_compartir:
				return False

			describedby = (input_compartir[0].get_attribute("aria-describedby") or "").split()
			ids_valor = [
				token for token in describedby
				if token.startswith("react-select-") and "-single-value" in token
			]
			for id_valor in ids_valor:
				for valor in driver.find_elements(By.ID, id_valor):
					if (valor.text or "").strip() == compartir_con:
						return True
			return False

		try:
			if not driver:
				return self.rpa_fail("Driver no inicializado para cambio de fecha.")

			email = str(getattr(self, "email_portal_asistencia", "") or "").strip()
			password = str(getattr(self, "password_portal_asistencia", "") or "").strip()

			obligatorios = [email, password, programa, fecha_inicio_dice, fecha_inicio_debe_decir, fecha_fin_dice, fecha_fin_debe_decir]
			if any(str(v).strip() == "" for v in obligatorios):
				return self.rpa_fail("Faltan datos obligatorios para cambio de fecha.")

			wait = WebDriverWait(driver, 25)

			print("[RPA][CAMBIO_FECHA] PASO 1: Abrir portal")
			driver.get(url_portal)
			wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

			print("[RPA][CAMBIO_FECHA] PASO 2/3: Login (si aplica)")
			ya_en_formulario = False
			try:
				wait.until(EC.visibility_of_element_located((By.ID, "summary")))
				ya_en_formulario = True
				print("[RPA][CAMBIO_FECHA] Formulario ya abierto; se omite login.")
			except Exception:
				pass

			if not ya_en_formulario:
				try:
					btn_login, xpath_login = self.buscarElemento(
						wait=wait,
						descripciones_xpath=[
							"//a[normalize-space()='Iniciar sesión']",
							"//a[contains(@href,'/servicedesk/customer/user/login')]"
						],
					)
					btn_login.click()
					print(f"[RPA][CAMBIO_FECHA] Click en iniciar sesión con selector: {xpath_login}")
				except (TimeoutException, NoSuchElementException):
					print("[RPA][CAMBIO_FECHA] No se encontró botón 'Iniciar sesión'; se intenta continuar si ya está autenticado.")

				try:
					input_email = wait.until(EC.visibility_of_element_located((By.ID, "user-email")))
					self.escribirInput(input_email, email)
					if input_email.get_attribute("value").strip() != str(email).strip():
						raise Exception("No se pudo validar escritura de email.")
					print("[RPA][CAMBIO_FECHA] Email ingresado y validado.")

					btn_siguiente, xpath_sig = self.buscarElemento(
						wait=wait,
						descripciones_xpath=[
							"//button[@id='login-button' and .//span[normalize-space()='Siguiente']]",
							"//button[@type='submit' and .//span[normalize-space()='Siguiente']]",
							"//button[@type='submit' and normalize-space()='Siguiente']"
						],
					)
					btn_siguiente.click()
					print(f"[RPA][CAMBIO_FECHA] Click en Siguiente con selector: {xpath_sig}")
				except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
					print(f"[RPA][CAMBIO_FECHA] Paso de email no aplicado (posible sesión activa): {e}")

				try:
					input_password, xpath_pass = self.buscarElemento(
						wait=wait,
						descripciones_xpath=[
							"//input[@id='user-password']",
							"//input[@data-testid='user-password']"
						],
					)
					self.escribirInput(input_password, password)
					if len(input_password.get_attribute("value") or "") == 0:
						raise Exception("No se pudo validar escritura de contraseña.")
					print(f"[RPA][CAMBIO_FECHA] Password ingresado y validado con selector: {xpath_pass}")

					btn_continuar, xpath_cont = self.buscarElemento(
						wait=wait,
						descripciones_xpath=[
							"//button[@id='login-button' and .//span[normalize-space()='Continuar']]",
							"//button[@type='submit' and .//span[normalize-space()='Continuar']]",
							"//button[@type='submit' and normalize-space()='Continuar']"
						],
					)
					btn_continuar.click()
					print(f"[RPA][CAMBIO_FECHA] Click en Continuar con selector: {xpath_cont}")
				except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
					print(f"[RPA][CAMBIO_FECHA] Paso de contraseña no aplicado (posible sesión activa): {e}")

				wait.until(
					lambda d: (
						("servicedesk/customer/portal" in (d.current_url or ""))
						or len(d.find_elements(By.ID, "summary")) > 0
						or len(d.find_elements(By.XPATH, "//a[contains(normalize-space(.),'Cambiar fecha de Actividad en Soporte Campus Virtual')]")) > 0
					)
				)

			print("[RPA][CAMBIO_FECHA] PASO 4: Abrir formulario")
			formulario_abierto = False
			try:
				wait.until(EC.visibility_of_element_located((By.ID, "summary")))
				formulario_abierto = True
			except TimeoutException:
				formulario_abierto = False

			if not formulario_abierto:
				link_form, xpath_form = self.buscarElemento(
					wait=wait,
					descripciones_xpath=[
						"//a[normalize-space()='Cambiar fecha de Actividad en Soporte Campus Virtual']",
						"//a[contains(@href,'/servicedesk/customer/portal/78/create/676')]"
					],
				)
				link_form.click()
				print(f"[RPA][CAMBIO_FECHA] Click en formulario con selector: {xpath_form}")

			wait.until(EC.visibility_of_element_located((By.ID, "customfield_10767")))
			wait.until(EC.visibility_of_element_located((By.ID, "summary")))

			print("[RPA][CAMBIO_FECHA] PASO 5: Nombre de la unidad")
			input_unidad = wait.until(EC.visibility_of_element_located((By.ID, "customfield_10767")))
			self.escribirInput(input_unidad, nombre_unidad)
			if input_unidad.get_attribute("value").strip() != nombre_unidad:
				raise Exception("No se pudo validar Nombre de la unidad.")

			print("[RPA][CAMBIO_FECHA] PASO 6: Nombre de la Actividad")
			input_programa = wait.until(EC.visibility_of_element_located((By.ID, "summary")))
			self.escribirInput(input_programa, programa)
			if input_programa.get_attribute("value").strip() != str(programa).strip():
				raise Exception("No se pudo validar Nombre de la Actividad.")

			print(f"[RPA][CAMBIO_FECHA] PASO 7: Compartir con = {compartir_con}")
			control_compartir, xpath_compartir = self.buscarElemento(
				wait=wait,
				descripciones_xpath=[
					"(//label[contains(normalize-space(.),'Compartir con')]/following::*[@role='combobox'][1])",
					"(//*[contains(normalize-space(.),'Compartir con')]/following::*[@role='combobox'][1])",
					"(//input[contains(@id,'react-select') and @aria-autocomplete='list'][1])"
				],
			)
			control_compartir.click()
			time.sleep(0.5)

			opcion_compartir, xpath_compartir_opcion = self.buscarElemento(
				wait=wait,
				descripciones_xpath=[
					f"//*[@role='option' and normalize-space()='{compartir_con}']",
					f"//*[contains(@id,'option') and normalize-space()='{compartir_con}']",
					f"//div[normalize-space()='{compartir_con}']"
				],
			)
			opcion_compartir.click()
			time.sleep(0.5)

			wait.until(lambda d: compartir_con_seleccionado())
			print(f"[RPA][CAMBIO_FECHA] Compartir con seleccionado usando {xpath_compartir} -> {xpath_compartir_opcion}")

			print("[RPA][CAMBIO_FECHA] PASO 8: Tipos de fechas")
			'''
			self.setCheckbox(
				driver=driver,
				wait=wait,
				etiqueta_log="Fecha de Inicio",
				lista_xpath=[
					"//input[@id='pf-undefined-cm-1-option-1' and @type='checkbox']",
					"//input[@type='checkbox' and @value='1']"
				],
				marcado=True
			)
			'''
			if fecha_inicio_dice != fecha_inicio_debe_decir:
				'''
				self.setCheckbox(
					driver=driver,
					wait=wait,
					etiqueta_log="Fecha de Inicio",
					lista_xpath=[
						"//label[contains(normalize-space(.),'Fecha de Inicio')]//preceding::input[@type='checkbox'][1]",
						"//label[contains(normalize-space(.),'Fecha de Inicio')]//following::input[@type='checkbox'][1]",
						"//*[contains(text(),'Fecha de Inicio')]/ancestor::*[1]//input[@type='checkbox']",
						"//input[contains(@id,'checkbox') and @type='checkbox']"
					],
					marcado=True
				)
				'''
				self.setCheckbox(
					driver=driver,
					wait=wait,
					etiqueta_log="Fecha de Inicio",
					lista_xpath=[
						"//label[.//span[normalize-space()='Fecha de Inicio']]//input[@type='checkbox']",
						"//span[normalize-space()='Fecha de Inicio']/ancestor::label//input[@type='checkbox']",
						"//input[@type='checkbox' and ancestor::label[.//span[normalize-space()='Fecha de Inicio']]]"
					],
					marcado=True
				)
				'''
				
				campo = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-8-select--control"]'
				)
				'''
				campo = wait.until(
					EC.element_to_be_clickable((
						By.CSS_SELECTOR,
						f'div[class*="-control"] input[id*="-da-"][id$="-8"]'
					))
				)

				driver.execute_script("arguments[0].click();", campo)

				time.sleep(0.5)
				'''
				input_fecha = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-8-select--input"]'
				)
				'''

				input_fecha = driver.find_element(
					By.CSS_SELECTOR,
					f'input[type="text"][role="combobox"][id*="-da-"][id$="-8"]'
				)

				# Limpiar
				input_fecha.send_keys(Keys.CONTROL, "a")
				input_fecha.send_keys(Keys.DELETE)

				time.sleep(0.3)

				# Escribir
				input_fecha.send_keys(fecha_inicio_dice)

				time.sleep(0.5)
				'''
				driver.save_screenshot(
					f"{SCREENSHOT_PATH}/fecha_test_1.png"
				)
				'''
				# Intentar confirmar
				input_fecha.send_keys(Keys.ENTER)

				time.sleep(1)

				'''
				driver.save_screenshot(
					f"{SCREENSHOT_PATH}/fecha_test_2.png"
				)
				'''

				# campo debe decir
				'''
				campo = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-9-select--control"]'
				)
				'''

				campo = wait.until(
					EC.element_to_be_clickable((
						By.CSS_SELECTOR,
						f'div[class*="-control"] input[id*="-da-"][id$="-9"]'
					))
				)

				driver.execute_script("arguments[0].click();", campo)

				time.sleep(0.5)
				'''
				input_fecha = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-9-select--input"]'
				)
				'''

				input_fecha = driver.find_element(
					By.CSS_SELECTOR,
					f'input[type="text"][role="combobox"][id*="-da-"][id$="-9"]'
				)


				# Limpiar
				input_fecha.send_keys(Keys.CONTROL, "a")
				input_fecha.send_keys(Keys.DELETE)

				time.sleep(0.3)

				# Escribir
				input_fecha.send_keys(fecha_inicio_debe_decir)

				time.sleep(0.5)
				'''
				driver.save_screenshot(
					f"{SCREENSHOT_PATH}/fecha_test_1.png"
				)
				'''
				# Intentar confirmar
				input_fecha.send_keys(Keys.ENTER)

				time.sleep(1)

				'''
				driver.save_screenshot(
					f"{SCREENSHOT_PATH}/fecha_test_2.png"
				)
				'''





			if fecha_fin_dice != fecha_fin_debe_decir:
				'''
				self.setCheckbox(
					driver=driver,
					wait=wait,
					etiqueta_log="Fecha de Fin",
					lista_xpath=[
						"//input[contains(@name,'Fecha de Fin') and @type='checkbox']",
						"//input[contains(@data-testid,'hidden-checkbox') and contains(@name,'Fecha de Fin')]",
						"//input[@type='checkbox' and contains(@name,'Fecha de Fin')]"
					],
					marcado=True
				)	
				'''
				self.setCheckbox(
					driver=driver,
					wait=wait,
					etiqueta_log="Fecha de Fin",
					lista_xpath=[
						"//label[.//span[normalize-space()='Fecha de Fin']]//input[@type='checkbox']",
						"//span[normalize-space()='Fecha de Fin']/ancestor::label//input[@type='checkbox']",
						"//input[@type='checkbox' and ancestor::label[.//span[normalize-space()='Fecha de Fin']]]"
					],
					marcado=True
				)
				'''
				campo = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-4-select--control"]'
				)
				'''
				campo = wait.until(
					EC.element_to_be_clickable((
						By.CSS_SELECTOR,
						f'div[class*="-control"] input[id*="-da-"][id$="-4"]'
					))
				)

				driver.execute_script("arguments[0].click();", campo)

				time.sleep(0.5)
				'''
				input_fecha = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-4-select--input"]'
				)
				'''
				input_fecha = driver.find_element(
					By.CSS_SELECTOR,
					f'input[type="text"][role="combobox"][id*="-da-"][id$="-4"]'
				)

				# Limpiar
				input_fecha.send_keys(Keys.CONTROL, "a")
				input_fecha.send_keys(Keys.DELETE)

				time.sleep(0.3)

				# Escribir
				print(fecha_fin_dice)
				input_fecha.send_keys(fecha_fin_dice)

				time.sleep(0.5)
				'''
				driver.save_screenshot(
					f"{SCREENSHOT_PATH}/fecha_test_1.png"
				)
				'''
				
				# Intentar confirmar
				input_fecha.send_keys(Keys.ENTER)

				time.sleep(1)

				'''
				driver.save_screenshot(
					f"{SCREENSHOT_PATH}/fecha_test_2.png"
				)
				'''

				# campo debe decir
				'''
				campo = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-5-select--control"]'
				)
				'''

				campo = wait.until(
					EC.element_to_be_clickable((
						By.CSS_SELECTOR,
						f'div[class*="-control"] input[id*="-da-"][id$="-5"]'
					))
				)

				driver.execute_script("arguments[0].click();", campo)

				time.sleep(0.5)
				'''
				input_fecha = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-5-select--input"]'
				)
				'''

				input_fecha = driver.find_element(
					By.CSS_SELECTOR,
					f'input[type="text"][role="combobox"][id*="-da-"][id$="-5"]'
				)


				# Limpiar
				input_fecha.send_keys(Keys.CONTROL, "a")
				input_fecha.send_keys(Keys.DELETE)

				time.sleep(0.3)

				# Escribir
				input_fecha.send_keys(fecha_fin_debe_decir)

				time.sleep(0.5)
				'''
				driver.save_screenshot(
					f"{SCREENSHOT_PATH}/fecha_test_3.png"
				)
				'''
				
				# Intentar confirmar
				input_fecha.send_keys(Keys.ENTER)

				time.sleep(1)

				'''
				driver.save_screenshot(
					f"{SCREENSHOT_PATH}/fecha_test_4.png"
				)
				'''
				
			#exit()
			'''
			self.setCheckbox(
				driver=driver,
				wait=wait,
				etiqueta_log="Fecha de Fin",
				lista_xpath=[
					"//input[@id='pf-undefined-cm-1-option-2' and @type='checkbox']",
					"//input[@type='checkbox' and @value='2']"
				],
				marcado=True
			)
			'''
			'''
			self.setCheckbox(
				driver=driver,
				wait=wait,
				etiqueta_log="Fecha de Fin",
				lista_xpath=[
					"//input[contains(@name,'Fecha de Fin') and @type='checkbox']",
					"//input[contains(@data-testid,'hidden-checkbox') and contains(@name,'Fecha de Fin')]",
					"//input[@type='checkbox' and contains(@name,'Fecha de Fin')]"
				],
				marcado=True
			)
			'''
			'''
			self.setCheckbox(
				driver=driver,
				wait=wait,
				etiqueta_log="Fecha de Cierre",
				lista_xpath=[
					"//input[@id='pf-undefined-cm-1-option-3' and @type='checkbox']",
					"//input[@type='checkbox' and @value='3']"
				],
				marcado=False
			)
			'''
			print("[RPA][CAMBIO_FECHA] PASO 9: Campos Fecha Inicio")
			'''
			formatos = [
				"30/03/2026",
				"03/30/2026",
				"3/30/2026",
				"30-03-2026",
				"2026-03-30",
				"Mar 30, 2026",
				"March 30, 2026",
				"30 Mar 2026",
			]

			for i, fecha in enumerate(formatos, start=1):

				print(f"\n=== PRUEBA {i}: {fecha} ===")

				# Abrir el control
				campo = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-8-select--control"]'
				)

				driver.execute_script("arguments[0].click();", campo)

				time.sleep(0.5)

				input_fecha = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-8-select--input"]'
				)

				# Limpiar
				input_fecha.send_keys(Keys.CONTROL, "a")
				input_fecha.send_keys(Keys.DELETE)

				time.sleep(0.3)

				# Escribir
				input_fecha.send_keys(fecha)

				time.sleep(0.5)
				driver.save_screenshot(
					f"{SCREENSHOT_PATH}/fecha_test_{i}1.png"
				)
				# Intentar confirmar
				input_fecha.send_keys(Keys.ENTER)

				time.sleep(1)

				# Leer visible
				visible = input_fecha.get_attribute("value")

				# Leer hidden
				hidden = driver.find_element(
					By.CSS_SELECTOR,
					'[data-testid="field-input-date-edit-8--input"]'
				).get_attribute("value")

				print("VISIBLE:", visible)
				print("HIDDEN :", hidden)

				driver.save_screenshot(
					f"{SCREENSHOT_PATH}/fecha_test_{i}.png"
				)
			'''
			
			'''

			f_inicio_dice = wait.until(EC.visibility_of_element_located((By.ID, "pf-93f18189-694f-49c2-b120-cc4f255209fc-date-8")))
			print(f_inicio_dice)
			self.escribirInput2(f_inicio_dice, fecha_inicio_dice)
			driver.save_screenshot(f"{SCREENSHOT_PATH}/ejemplo.png")#ELIMINAR EN PARTE FINAL
			hidden = driver.find_element(
				By.CSS_SELECTOR,
				'[data-testid="field-input-date-edit-8--input"]'
			)

			print("HIDDEN:", hidden.get_attribute("value"))
			
			if (f_inicio_dice.get_attribute("value") or "").strip() != str(fecha_inicio_dice).strip():
				raise Exception("No se pudo validar 'Dice' de Fecha Inicio.")
			
			f_inicio_debe = wait.until(EC.visibility_of_element_located((By.ID, "pf-93f18189-694f-49c2-b120-cc4f255209fc-date-9")))
			self.escribirInput2(f_inicio_debe, fecha_inicio_debe_decir)
			
			if (f_inicio_debe.get_attribute("value") or "").strip() != str(fecha_inicio_debe_decir).strip():
				raise Exception("No se pudo validar 'Debe decir' de Fecha Inicio.")
			
			print("[RPA][CAMBIO_FECHA] PASO 10: Campos Fecha Fin")
			f_fin_dice = wait.until(EC.visibility_of_element_located((By.ID, "pf-93f18189-694f-49c2-b120-cc4f255209fc-date-4")))
			self.escribirInput2(f_fin_dice, fecha_fin_dice)
			
			if (f_fin_dice.get_attribute("value") or "").strip() != str(fecha_fin_dice).strip():
				raise Exception("No se pudo validar 'Dice' de Fecha Fin.")
			
			f_fin_debe = wait.until(EC.visibility_of_element_located((By.ID, "pf-93f18189-694f-49c2-b120-cc4f255209fc-date-5")))
			self.escribirInput2(f_fin_debe, fecha_fin_debe_decir)
			
			if (f_fin_debe.get_attribute("value") or "").strip() != str(fecha_fin_debe_decir).strip():
				raise Exception("No se pudo validar 'Debe decir' de Fecha Fin.")
			'''
			print("[RPA][CAMBIO_FECHA] PASO 11: Motivo de la Solicitud")
			editor_motivo, xpath_editor = self.buscarElemento(
				wait=wait,
				descripciones_xpath=[
					"//*[contains(normalize-space(.),'Motivo de la Solicitud')]/following::*[@contenteditable='true'][1]",
					"//div[@contenteditable='true' and @role='textbox'][1]",
					"//*[@contenteditable='true'][1]"
				],
			)
			editor_motivo.click()
			editor_motivo.send_keys(Keys.CONTROL, "a")
			editor_motivo.send_keys(Keys.DELETE)
			editor_motivo.send_keys(motivo_solicitud)
			time.sleep(0.6)
			texto_editor = (editor_motivo.text or "").strip()
			if motivo_solicitud not in texto_editor:
				raise Exception("No se pudo validar texto de Motivo de la Solicitud.")
			print(f"[RPA][CAMBIO_FECHA] Motivo ingresado usando selector: {xpath_editor}")

			print("[RPA][CAMBIO_FECHA] PASO 12: Validación final antes de enviar")
			'''
			validaciones = [
				(input_unidad.get_attribute("value") or "").strip() == nombre_unidad,
				(input_programa.get_attribute("value") or "").strip() == str(programa).strip(),
				compartir_con_seleccionado(),
				wait.until(EC.presence_of_element_located((By.ID, "pf-undefined-cm-1-option-1"))).is_selected(),
				wait.until(EC.presence_of_element_located((By.ID, "pf-undefined-cm-1-option-2"))).is_selected(),
				not wait.until(EC.presence_of_element_located((By.ID, "pf-undefined-cm-1-option-3"))).is_selected(),
				(f_inicio_dice.get_attribute("value") or "").strip() == str(fecha_inicio_dice).strip(),
				(f_inicio_debe.get_attribute("value") or "").strip() == str(fecha_inicio_debe_decir).strip(),
				(f_fin_dice.get_attribute("value") or "").strip() == str(fecha_fin_dice).strip(),
				(f_fin_debe.get_attribute("value") or "").strip() == str(fecha_fin_debe_decir).strip(),
				motivo_solicitud in (editor_motivo.text or "")
			]
			if not all(validaciones):
				return self.rpa_fail("Validación final fallida. No se enviará el formulario.")
			'''
			print("[RPA][CAMBIO_FECHA] PASO 13: Envío")
			boton_enviar, xpath_enviar = self.buscarElemento(
				wait=wait,
				descripciones_xpath=[
					"//button[@data-testid='request-create-form-submit-button']",
					"//button[@type='submit' and .//span[normalize-space()='Enviar']]",
					"//button[@type='submit' and normalize-space()='Enviar']"
				],
			)
			driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton_enviar)
			print(f"[RPA][CAMBIO_FECHA] Botón Enviar ubicado con selector: {xpath_enviar}")

			try:
				boton_enviar.click()
			except Exception:
				driver.execute_script("arguments[0].click();", boton_enviar)

			try:
				wait.until(lambda d: "create/676" not in (d.current_url or ""))
			except Exception as e:
				return self.rpa_fail("No se logró enviar el formulario de cambio de fechas.", e)

			resumen = {
				"status": "sent",
				"message": "Formulario enviado correctamente.",
				"final_url": driver.current_url,
				"campos_enviados": campos_enviados
			}

			
			try:
				self.enviarCorreoCambioFecha(
					nombre_programa=str(programa or "").strip(),
					campus_ini=fecha_correo_ini_dice,
					campus_fin=fecha_correo_fin_dice,
					dt_ini=fecha_correo_ini_debe,
					dt_fin=fecha_correo_fin_debe
				)
			except Exception as e_mail:
				print("[RPA][CAMBIO_FECHA][WARN] Formulario enviado, pero falló correo de confirmación:", e_mail)
			
			print("[RPA][CAMBIO_FECHA] Resultado:", json.dumps(resumen, ensure_ascii=False))
			
			resultado.estado = 1
			resultado.error = 0
			resultado.continua = True
			resultado.mensaje_status = json.dumps(resumen, ensure_ascii=False)
			return resultado

		except TimeoutException as e:
			return self.rpa_fail("Timeout en flujo cambiarFechasActividad: {}".format(e))
		except Exception as e:
			error_payload = {
				"status": "error",
				"message": str(e),
				"final_url": (driver.current_url if driver else None),
				"campos_enviados": campos_enviados
			}
			print("[RPA][CAMBIO_FECHA][ERROR]", json.dumps(error_payload, ensure_ascii=False))
			return self.rpa_fail("Flujo cambio fecha falló: {}".format(e))


	def logInCampusVirtualRaes(self, driver='', usuario_exec=''):
		driver.get(f"{self.url_pandora}/pucp/login")
		wait = WebDriverWait(driver, 10)

		if usuario_exec=='alberto':
			usuario = self.user_pago_alb
			password = self.pass_pago_alb
		else:
			usuario = self.user_pago
			password = self.pass_pago
		
		username_input =  WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
		)
		username_input.send_keys(usuario)
		password_input =  WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
		)
		password_input.send_keys(password)
		submit_login_button = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@class='submit izq']"))
		)
		
		submit_login_button.click()

		try:
			wait.until(
				lambda d:
					d.find_elements(By.XPATH, "//div[contains(@class,'cierre-correcto')]") 
			)
		except TimeoutException:
			#emails = 'abarbozab@pucp.pe'
			#Colocar correo de manuel tambien
			emails = [self.email]
			cc = [] 
			bcc = [self.bcc]

			subject = 'FALLO VALIDACIÓN INICIO DE SESIÓN RPA SISTEMA DE EVALUACIÓN NO GRADO FUNCION PAGOS'
			from_address = "Plataforma-Centrum <noreply@centrummailing.pucp.edu.pe>"

			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)       

			if cc:
				msg['Cc'] = ", ".join(cc)      

			msg['Subject'] = subject
			text_email_student = f"""
							<html>
							<body>
								<p>Estimados,</p>
								<p>El RPA de creación de sistema de evaluación no pudo iniciar sesión en el Campus Virtual.</p>
							</body>
							</html>
							"""     
			msg.attach(MIMEText(text_email_student, 'html'))

			msg_string = msg.as_string()

			toaddrs = emails + cc + bcc         

			
			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			#text = msg.as_string()
			server.sendmail(from_address, toaddrs, msg_string)
			server.quit()
			print("No se pudo validar el login: no se encontró ni 'cierre-correcto', "
				"ni 'tabParticipando', ni el formulario de login.")
			'''
			raise RuntimeError(
				"No se pudo validar el login: no se encontró ni 'cierre-correcto', "
				"ni 'tabParticipando', ni el formulario de login."
			)
			'''

		if driver.find_elements(By.XPATH, "//div[contains(@class,'cierre-correcto')]"):
			print("[RPA] Login correcto (pantalla 'Inicio de sesión correcto').")
			return driver

		print("Estado de login indeterminado tras enviar el formulario.")
		#raise RuntimeError("Estado de login indeterminado tras enviar el formulario.")
	
	def validarSistemaEvaluacion(self, driver=''):

		wait = WebDriverWait(driver, 10)
		resultado = ResultadoRPA()

		try:

			# Caso: NO tiene sistema evaluación
			try:
				wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//td[@class='pucpTitulo' and contains(text(),'No se ha registrado la forma de calificación')]"
            	)))

				print("[RPA] No tiene sistema de evaluación")
				resultado.estado = 0
				resultado.error = 0
				resultado.mensaje_error = "No tiene sistema evaluación"
				resultado.continua = True
				return resultado

			except TimeoutException:
				pass


			# Caso: SI tiene sistema evaluación
			try:
				wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//td[@class='pucpSubTitulo' and contains(text(),'Evaluaciones registradas')]"
            	)))

				print("[RPA] Tiene sistema de evaluación")
				resultado.estado = 1
				resultado.error = 0
				resultado.mensaje_error = "Tiene sistema evaluación"
				resultado.continua = True
				return resultado

			except TimeoutException:
				pass


			print("[RPA] No se pudo determinar el estado")
			resultado.estado = 2
			resultado.error = 0
			resultado.mensaje_error = "Estado desconocido"
			resultado.continua = False
			return resultado


		except Exception as e:
			print("[RPA][ERROR]", e)
			resultado.estado = 2
			resultado.error = 1
			resultado.mensaje_error = str(e)
			resultado.continua = False
			return resultado
	
	def enviarCorreoSistemaEvaluacion(self, df):

		try:

			if df.empty:
				print("[RPA] No hay correos para enviar")
				return

			agrupado = df.groupby("email")

			for email, cursos in agrupado:

				teacher = cursos.iloc[0]["full_name"]
				emails = [e.strip() for e in self.emailvalideval.split(",")]
				
				cc = []
				bcc = [self.bcc]

				subject = f"📢 Importante: Cursos sin Sistema de Evaluación en Campus Virtual - {teacher}"
				from_address = "Plataforma-Centrum <noreply@centrummailing.pucp.edu.pe>"

				msg = MIMEMultipart()
				msg['From'] = from_address
				msg['To'] = ", ".join(emails)
				if cc:
					msg['Cc'] = ", ".join(cc)
				msg['Subject'] = subject


				contenido = ""

				for idx, row in cursos.iterrows():

					fecha = datetime.strptime(row['registration_date'], "%Y-%m-%d").strftime("%d/%m/%Y")

					contenido += f"""
					<tr>
						<td style="padding:10px;">{row['program_name']}</td>
						<td style="padding:10px;">{row['course_name']}</td>
						<td style="padding:10px;">{row['cycle_name']}</td>
						<td style="padding:10px;">{fecha}</td>
					</tr>
					"""
				html = f"""
				<!DOCTYPE html>
				<html>
				<head>
				<meta charset="utf-8">
				<title>Registro CentrumX</title>
				</head>
				<body>
					<table align="center" border="0" cellpadding="0" cellspacing="0" height="100%" width="100%"
						style="border-collapse: collapse;height: 100%;margin: 0;padding: 0;width: 100%;background-color: #ffffff;">
						<tr>
							<td align="center" valign="top" style="height: 100%;margin: 0;padding: 0;width: 100%;border-top: 0;">
								<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:collapse;" width="100%">
									<tr>
									<td align="center" 
											style="background-color: rgb(76, 170, 216);
											background-image: url('https://centrumwebs.pucp.edu.pe/cisam/public/img/modulo/header_image.jpg');
											background-repeat: no-repeat; background-position: center center;
											background-size: cover; border-top: 0px border-bottom 0px; padding-top: 20px;
											padding-bottom: 20px;" valign="top">
											<table align="center" border="0" cellpadding="0" cellspacing="0" style="border-collapse: 
											collapse;max-width: 600px !important;" width="100%"> 
												<tr>
													<td valign="top">
														<table border="0" cellpadding="0" cellspacing="0" width="100%"
															style="min-width: 100%;border-collapse: collapse;">
															<tr>
																<td style="padding:0px" valign="top">
																	<table align="left" border="0" cellpadding="0" cellspacing="0"
																	style="min-width: 100%; border-collapse: collapse;" width="100%">
																		<tr>
																			<td valign="top" style="padding-right:0px;padding-left:0px;padding-top:0;padding-bottom:0;text-align:center;">
																			<span style="float:none;display:block;text-align:center;">
																					<img align="middle" alt="" height="68" src="https://centrumwebs.pucp.edu.pe/cisam/public/img/login/logo-blanco.png" 
																						style="max-width:254px;padding-bottom:0px;vertical-align:bottom;display:inline!important;width:220px;height:68px;border:0;outline:none;text-decoration:none;" 
																						width="220" processed="true">
																				</span>   
																			</td>
																		</tr>
																	</table>
																</td>
															</tr>
														</table>
													</td>
												</tr>
											</table>
										</td> 
									</tr>
									<tr>
										<td align="center" valign="top"
											style="background-color:#ffffff;background-image:none;background-repeat:no-repeat;
											background-position:center;background-size:cover;border-top:0;border-bottom:0;
											padding-top:20px;padding-bottom:0px;">
											<table align="center" border="0" cellpadding="0" cellspacing="0" 
												style="border-collapse:collapse;max-width:600px!important" width="100%">
												<tr>
													<td style="padding:0 20px 10px;color:#174275;font-size:15px;">
													<p>Estimado equipo de Registro Académico</p>

													<p>
													Se ha detectado que aún no se han configurado los sistemas de evaluación
													del siguiente profesor <b>{teacher}</b> en los cursos detallados a continuación:
													</p>
													</td>
												</tr>
												<tr>
													<td style="padding:0 20px 20px;">
													<table width="100%" cellpadding="0" cellspacing="0"
														style="border:1px solid #d9e6f2;border-radius:6px;
														border-collapse:separate;overflow:hidden;">

														<tr style="background:#174275;color:#ffffff;">
															<th align="left" style="padding:10px;">Programa</th>
															<th align="left" style="padding:10px;">Curso</th>
															<th align="left" style="padding:10px;">Ciclo</th>
															<th align="left" style="padding:10px;">F.Limite Reg. Notas</th>
														</tr>

														{contenido}

													</table>
													</td>
												</tr>
												<tr>
													<td style="padding:0 20px 20px;color:#174275;font-size:14px;">
														<p>
														Por favor configurar el Sistema de Evaluación a la brevedad posible.
														</p>

														<p style="color:#6b7a90;font-size:12px;">
														Mensaje generado automáticamente por el RPA de Validación de Sistema de Evaluación.
														</p>
													</td>
												</tr>
											</table>
										</td>
									</tr>
								</table>
							</td>
						</tr>
					</table>
				</body>
				</html>

				"""

				

				msg.attach(MIMEText(html, 'html'))

				msg_string = msg.as_string()
				toaddrs = emails + cc + bcc

				server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
				server.starttls()
				server.login(self.smpt_user, self.smpt_pass)

				print(from_address, toaddrs)

				server.sendmail(from_address, toaddrs, msg_string)
				server.quit()

				print(f"[RPA][MAIL] Correo enviado: {email}")
				

		except Exception as e:
			print(f"[RPA][WARN] No se pudo enviar correo: {e}")

	

	def enviarCorreoCambioFecha(self, nombre_programa, campus_ini, campus_fin, dt_ini, dt_fin):
		try:
			emails = [e.strip() for e in self.emails_cert.split(",")]
			cc = []
			bcc = [self.bcc]

			subject = f"Importante: Solicitud de cambio de fecha enviada - {nombre_programa}"
			from_address = "Plataforma-Centrum <noreply@centrummailing.pucp.edu.pe>"

			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)
			if cc:
				msg['Cc'] = ", ".join(cc)
			msg['Subject'] = subject

			html = f"""
			<html>
			<body style="margin:0;padding:0;background:#f4f7fb;
						font-family:Arial,Helvetica,sans-serif;">
				<table width="100%" cellpadding="0" cellspacing="0"
					style="background:#f4f7fb;padding:20px 0;">
					<tr>
						<td align="center">

							<table width="680" cellpadding="0" cellspacing="0"
								style="background:#ffffff;border:1px solid #d9e6f2;
								border-radius:8px;overflow:hidden;">

								<tr>
									<td style="background:#174275;color:#ffffff;
											padding:14px 20px;font-size:16px;font-weight:bold;">
										Solicitud de Cambio de Fecha Enviada a la plataforma de la DEC. Plataforma JIRA.
									</td>
								</tr>

								<tr>
									<td style="padding:20px;color:#1f2d3d;font-size:14px;line-height:1.5;">
										<p style="margin:0 0 12px 0;">Estimados,</p>
										<p style="margin:0 0 12px 0;">
											Se envió correctamente la solicitud de cambio de fecha para el programa:
										</p>
										<div style="background:#eef4fb;border:1px solid #d9e6f2;
													border-radius:6px;padding:12px;margin:10px 0;">
											<strong>{nombre_programa}</strong>
										</div>
									</td>
								</tr>

								<tr>
									<td style="padding:0 20px 20px;">
										<table width="100%" cellpadding="0" cellspacing="0"
											style="border:1px solid #d9e6f2;border-radius:6px;
											border-collapse:separate;overflow:hidden;">
											<tr style="background:#174275;color:#ffffff;">
												<th align="left" style="padding:10px;">Origen</th>
												<th align="left" style="padding:10px;">Fecha inicio</th>
												<th align="left" style="padding:10px;">Fecha fin</th>
											</tr>
											<tr>
												<td style="padding:10px;">Campus Virtual</td>
												<td style="padding:10px;">{campus_ini}</td>
												<td style="padding:10px;">{campus_fin}</td>
											</tr>
											<tr>
												<td style="padding:10px;">Último Horario Registrado</td>
												<td style="padding:10px;">{dt_ini}</td>
												<td style="padding:10px;">{dt_fin}</td>
											</tr>
										</table>
									</td>
								</tr>

								<tr>
									<td style="padding:0 20px 20px;color:#174275;font-size:14px;">
										<p style="margin:0 0 8px 0;">
											Ya se solicitó el cambio de fecha en el portal de soporte.
										</p>
										<p style="margin:0;color:#6b7a90;font-size:12px;">
											Mensaje generado automáticamente por el RPA de Certificación Digital.
										</p>
									</td>
								</tr>

							</table>

						</td>
					</tr>
				</table>
			</body>
			</html>
			"""
			msg.attach(MIMEText(html, 'html'))

			msg_string = msg.as_string()
			toaddrs = emails + cc + bcc

			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			server.sendmail(from_address, toaddrs, msg_string)
			server.quit()

			print(f"[RPA][MAIL] Correo enviado: solicitud de cambio de fecha enviada ({nombre_programa})")
		except Exception as e:
			print(f"[RPA][WARN] No se pudo enviar correo de confirmación de cambio de fecha ({nombre_programa}): {e}")
	

	def enviarCorreoFechasDistintas(self, codigo_programa, campus_ini, campus_fin, dt_ini, dt_fin):
		
		try:
			#emails = [self.email]
			emails = [e.strip() for e in self.emails_cert.split(",")]
			cc = []
			bcc = [self.bcc]

			subject = f"Importante: Fechas distintas en Configuración de Certificación Digital - {codigo_programa}"
			from_address = "Plataforma-Centrum <noreply@centrummailing.pucp.edu.pe>"

			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)
			if cc:
				msg['Cc'] = ", ".join(cc)
			msg['Subject'] = subject
			
			html = f"""
			<!DOCTYPE html>
			<html>
			<head>
			<meta charset="utf-8">
			<title>Alerta de Fechas Distintas</title>
			</head>
			<body>
			<table align="center" width="100%" cellpadding="0" cellspacing="0"
				style="background-color:#ffffff;font-family:Helvetica,Arial,sans-serif;">
				<tr>
				<td align="center">

					<table width="100%" cellpadding="0" cellspacing="0"
					style="background-image:url('https://centrumwebs.pucp.edu.pe/cisam/public/img/modulo/header_image.jpg');
					background-size:cover;background-position:center;padding:20px 0;">
					<tr>
						<td align="center">
						<img src="https://centrumwebs.pucp.edu.pe/cisam/public/img/login/logo-blanco.png"
							width="220" height="68" alt="CENTRUM PUCP"
							style="display:block;border:0;">
						</td>
					</tr>
					</table>

					<table width="600" cellpadding="0" cellspacing="0"
					style="background:#ffffff;margin-top:20px;border-collapse:collapse;">

					<tr>
						<td style="padding:20px;color:#174275;font-size:18px;">
						<strong>Importante: Fechas distintas en Certificación Digital</strong>
						</td>
					</tr>

					<tr>
						<td style="padding:0 20px 10px;color:#174275;font-size:15px;">
						<p>Estimados,</p>
						<p>
							No es posible continuar con la configuración de
							<strong>Certificación Digital</strong> para:
						</p>

						<div style="background:#f4f8fc;border:1px solid #d9e6f2;
							border-radius:6px;padding:12px;margin:10px 0;">
							<strong>{codigo_programa}</strong>
						</div>

						<p>
							Motivo: se detectaron <strong>fechas distintas</strong>
							entre Campus Virtual y el último horario registrado.
						</p>
						</td>
					</tr>

					<tr>
						<td style="padding:0 20px 20px;">
						<table width="100%" cellpadding="0" cellspacing="0"
							style="border:1px solid #d9e6f2;border-radius:6px;
							border-collapse:separate;overflow:hidden;">
							<tr style="background:#174275;color:#ffffff;">
							<th align="left" style="padding:10px;">Origen</th>
							<th align="left" style="padding:10px;">Fecha inicio</th>
							<th align="left" style="padding:10px;">Fecha fin</th>
							</tr>
							<tr>
							<td style="padding:10px;">Campus Virtual</td>
							<td style="padding:10px;">{campus_ini}</td>
							<td style="padding:10px;">{campus_fin}</td>
							</tr>
							<tr>
							<td style="padding:10px;">Último Horario Registrado</td>
							<td style="padding:10px;">{dt_ini}</td>
							<td style="padding:10px;">{dt_fin}</td>
							</tr>
						</table>
						</td>
					</tr>

					<tr>
						<td style="padding:0 20px 20px;color:#174275;font-size:14px;">
						<p>
							Por favor, corregir las fechas para que coincidan y
							volver a ejecutar el RPA.
						</p>
						<p style="color:#6b7a90;font-size:12px;">
							Mensaje generado automáticamente por el RPA de Certificación Digital.
						</p>
						</td>
					</tr>

					</table>

				</td>
				</tr>
			</table>
			</body>
			</html>
			"""

			msg.attach(MIMEText(html, 'html'))

			msg_string = msg.as_string()
			toaddrs = emails + cc + bcc

			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			print(from_address, toaddrs)
			server.sendmail(from_address, toaddrs, msg_string)
			server.quit()

			print(f"[RPA][MAIL] Correo enviado por fechas distintas: {codigo_programa}")

		except Exception as e:
			
			print(f"[RPA][WARN] No se pudo enviar correo de fechas distintas ({codigo_programa}): {e}")


	def logInCampusVirtualCiclo1(self, driver=''):
		driver.get(f"{self.url_pandora}/pucp/login")
		wait = WebDriverWait(driver, 10)

		usuario = self.usereval
		password = self.passeval
		
		username_input =  WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
		)
		username_input.send_keys(usuario)
		password_input =  WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
		)
		password_input.send_keys(password)
		submit_login_button = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[@class='submit izq']"))
		)
		
		submit_login_button.click()

		try:
			wait.until(
				lambda d:
					d.find_elements(By.XPATH, "//div[contains(@class,'cierre-correcto')]") 
			)
		except TimeoutException:
			emails = [self.email]
			cc = [] 
			bcc = [self.bcc]

			subject = 'FALLO VALIDACIÓN INICIO DE SESIÓN RPA SISTEMA DE EVALUACIÓN NO GRADO'
			from_address = "Plataforma-Centrum <noreply@centrummailing.pucp.edu.pe>"

			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)       

			if cc:
				msg['Cc'] = ", ".join(cc)      

			msg['Subject'] = subject
			text_email_student = f"""
							<html>
							<body>
								<p>Estimados,</p>
								<p>El RPA de creación de sistema de evaluación no pudo iniciar sesión en el Campus Virtual.</p>
							</body>
							</html>
							"""     
			msg.attach(MIMEText(text_email_student, 'html'))

			msg_string = msg.as_string()

			toaddrs = emails + cc + bcc         

			
			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			server.sendmail(from_address, toaddrs, msg_string)
			server.quit()
			print("No se pudo validar el login: no se encontró ni 'cierre-correcto', "
				"ni 'tabParticipando', ni el formulario de login.")
			'''
			raise RuntimeError(
				"No se pudo validar el login: no se encontró ni 'cierre-correcto', "
				"ni 'tabParticipando', ni el formulario de login."
			)
			'''

		if driver.find_elements(By.XPATH, "//div[contains(@class,'cierre-correcto')]"):
			print("[RPA] Login correcto (pantalla 'Inicio de sesión correcto').")
			return driver

		print("Estado de login indeterminado tras enviar el formulario.")
		#raise RuntimeError("Estado de login indeterminado tras enviar el formulario.")


	def enviarCorreoCodigoDuplicados(self, grupos_programas):
		try:
			# Preparar destinatariosel jueves 
			emails = [e.strip() for e in self.emailvaldupli.split(",")]
			cc = []
			bcc = []
   		#bcc = [self.bcc]
			# Calcular totales
			total_programas = len(grupos_programas)
			total_solicitudes = sum(len(sols) for sols in grupos_programas.values())

			# Subject
			subject = f" Códigos Duplicados Detectados - {total_programas} programa(s)"
			from_address = "RPA Matricula CENTRUM <noreply@centrummailing.pucp.edu.pe>"
			# Crear mensaje
			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)
			if cc:
				msg['Cc'] = ", ".join(cc)
			msg['Subject'] = subject
			#URL base CISAM desde config
			url_eros = config['url']['eros']
			# Construir tabla por programa
			filas_programas = ""
			for programa, solicitudes in grupos_programas.items():
				cant_solicitudes = len(solicitudes)
				# Tomar el primer idproceso
				idproceso = solicitudes[0]['idproceso']
				# Link para revisar en CV
				link_revision = f"{url_eros}/pucp/oca/oawadmin/oawadmin?accion=RevisarCodigosDuplicados&codProceso={idproceso}" #falta modificar 
				filas_programas += f"""
				<tr>
					<td style="padding:14px;border-bottom:1px solid #e8e8e8;font-weight:600;color:#174275;">
						{programa}
					</td>
					<td style="padding:14px;border-bottom:1px solid #e8e8e8;text-align:center;">
						<a href="{link_revision}" style="background:#174275;color:#ffffff;padding:10px 20px;text-decoration:none;border-radius:4px;display:inline-block;font-weight:600;font-size:13px;">
							🔍 Revisar Códigos
						</a>
					</td>
				</tr>
				"""
			# HTML del correo
			html = f"""
			<html>
				<body style="margin:0;padding:0;background:#f4f7fb;font-family:Arial,Helvetica,sans-serif;">
					<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f7fb;padding:20px 0;">
						<tr>
							<td align="center">
								<table width="750" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #d9e6f2; border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
									<!-- Header -->
										<tr>
											<td style="background:#174275;color:#ffffff;padding:20px;text-align:center;">
												<h1 style="margin:0;font-size:22px;font-weight:600;">
													⚠️ Códigos Duplicados Detectados
												</h1>
												<p style="margin:8px 0 0 0;font-size:14px;opacity:0.9;">
													Revisión requerida en Campus Virtual
												</p>
											</td>
										</tr>
									<!-- Resumen -->
										<tr>
											<td style="padding:25px;">
												<div style="background:#fff3cd;border-left:4px solid #ffc107; padding:16px;margin-bottom:20px;border-radius:4px;">
													<p style="margin:0;font-size:15px;color:#856404;line-height:1.6;">
														<strong>📊 Resumen:</strong>
															<br>
																Se detecto código(s) duplicado(s) en <strong>{total_programas} programa(s)</strong>.
															<br>
														<span style="font-size:13px;margin-top:6px;display:block;">
															Por favor, verifique los códigos duplicados en el sistema antes de continuar con la generación de códigos.
														</span>
  												</p>
												</div>
											</td>
										</tr>
                            
									<!-- Tabla de programas -->
										<tr>
											<td style="padding:0 25px 25px;">
												<table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #d9e6f2;border-radius:6px; border-collapse:separate;overflow:hidden;">
													<tr style="background:#174275;color:#ffffff;">
														<th align="left" style="padding:14px;font-weight:600;font-size:14px;">
															 Programa
														</th>
														<th align="center" style="padding:14px;font-weight:600;font-size:14px;width:180px;">
															Acción
														</th>
													</tr>
													{filas_programas}
												</table>
											</td>
										</tr>
                            
									<!-- Instrucciones -->
										<tr>
											<td style="padding:0 25px 25px;">
												<div style="background:#e7f3ff;border:1px solid #b3d9ff; border-radius:6px;padding:18px;">
													<p style="margin:0 0 12px 0;font-weight:600;color:#174275;font-size:15px;">
														🔧 Cómo resolver:
													</p>
													<ol style="margin:0;padding-left:20px;color:#495057;line-height:1.8;font-size:14px;">
														<li style="margin-bottom:8px;">
															Ingresar al Campus Virtual
														</li>
														<li style="margin-bottom:8px;">
															Haz clic en <strong>"🔍 Revisar Códigos"</strong> para el programa correspondiente
														</li>
														<li style="margin-bottom:8px;">
															Verifica los códigos duplicados en el listado
														</li>
														<li>
															El proceso de generación de códigos se reanudará automáticamente una vez corregido
														</li>
													</ol>
												</div>
											</td>
										</tr>
                            
									<!-- Footer -->
										<tr>
											<td style="padding:20px 25px;background:#f8f9fa;border-top:1px solid #e8e8e8;">
												<p style="margin:0;color:#6b7a90;font-size:12px;line-height:1.6;">
													<strong>🤖 Notificación automática</strong> del RPA de Matrícula CENTRUM<br>
													Fecha: <strong>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</strong><br>
													<span style="color:#999;">
														Este reporte se genera cuando se detectan códigos duplicados durante el proceso de matrícula.
													</span>
												</p>
											</td>
										</tr>
								</table>
							</td>
						</tr>
					</table>
				</body>
			</html>
			"""
			
			msg.attach(MIMEText(html, 'html'))
			msg_string = msg.as_string()
			toaddrs = emails + cc + bcc

			# Enviar correo
			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			server.sendmail(from_address, toaddrs, msg_string)
			server.quit()

			print(f"[RPA][MAIL] ✅ Correo consolidado enviado: {total_programas} programas, {total_solicitudes} casos")
			return True
		except Exception as e:
			print(f"[RPA][WARN] ❌ No se pudo enviar correo de códigos duplicados: {e}")
			import traceback
			traceback.print_exc()
			return False
		
	def enviarCorreoValidacionAnho(self, grupos_programas):
		try:
			emails = [e.strip() for e in self.emailvalanho.split(",")]
			cc = []
			bcc = []
			# Calcular totales
			total_programas = len(grupos_programas)
			subject = f"Años Incorrectos Detectados - {total_programas} programa(s)"
			from_address = "RPA Matricula CENTRUM <noreply@centrummailing.pucp.edu.pe>"
			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)
			if cc:
				msg['Cc'] = ", ".join(cc)
			msg['Subject'] = subject
			url_eros = config['url']['eros']
			filas_programas = ""
			for programa, solicitudes in grupos_programas.items():
				for sol in solicitudes:
					idproceso  = sol['idproceso']
					anho_cisam = sol['anho_cisam']
					link_revision = f"{url_eros}/pucp/oca/oawadmin/oawadmin?accion=AbrirProceso&codProceso={idproceso}"

					# Construir detalle de errores según fuente
					detalle_errores = ""
					if sol['error_gencodigo'] is not None:
						detalle_errores += f"""
						<td style="background:#fff3cd;border-left:3px solid #ffc107;padding:8px 12px;margin-bottom:6px;border-radius:3px;font-size:13px;">
							<strong>📄 Generación de Códigos:</strong>
							Año esperado <strong>{anho_cisam}</strong> — encontrado <strong>{sol['error_gencodigo']}</strong>
						</td>
						"""
					if sol['error_procesadmi'] is not None:
						detalle_errores += f"""
						<td style="background:#f8d7da;border-left:3px solid #dc3545;padding:8px 12px;margin-bottom:6px;border-radius:3px;font-size:13px;">
							<strong>📋 Proceso de Admisión:</strong>
							Año esperado <strong>{anho_cisam}</strong> — encontrado <strong>{sol['error_procesadmi']}</strong>
						</td>
						"""

					filas_programas += f"""
					<tr>
						<td style="padding:14px;border-bottom:1px solid #e8e8e8;font-weight:600;color:#174275;">
						    {programa}
						</td>
						
						    {detalle_errores}
						
						
					</tr>
					"""
			html = f"""
				<html>
					<body style="margin:0;padding:0;background:#f4f7fb;font-family:Arial,Helvetica,sans-serif;">
						<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f7fb;padding:20px 0;">
							<tr>
								<td align="center">
									<table width="750" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #d9e6f2;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
										<!-- Header -->
										<tr>
											<td style="background:#174275;color:#ffffff;padding:20px;text-align:center;">
												<h1 style="margin:0;font-size:22px;font-weight:600;">
													⚠️ Años Incorrectos Detectados
												</h1>
												<p style="margin:8px 0 0 0;font-size:14px;opacity:0.9;">
													Revisión requerida en Campus Virtual
												</p>
											</td>
										</tr>
										<!-- Resumen -->
										<tr>
											<td style="padding:25px;">
												<div style="background:#fff3cd;border-left:4px solid #ffc107;padding:16px;margin-bottom:20px;border-radius:4px;">
													<p style="margin:0;font-size:15px;color:#856404;line-height:1.6;">
														<strong>📊 Resumen:</strong>
														<br>
														Se detectó año incorrecto en <strong>{total_programas} programa(s)</strong>.
														<br>
														<span style="font-size:13px;margin-top:6px;display:block;">
															Por favor, verifique y corrija el año en el proceso de admisión correspondiente.
														</span>
													</p>
												</div>
											</td>
										</tr>
										<!-- Tabla de programas -->
										<tr>
											<td style="padding:0 25px 25px;">
												<table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #d9e6f2;border-radius:6px;border-collapse:separate;overflow:hidden;">
													<tr style="background:#174275;color:#ffffff;">
														<th align="left" style="padding:14px;font-weight:600;font-size:14px;">
															Proceso de Admisión
														</th>
														<th align="center" style="padding:14px;font-weight:600;font-size:14px;width:120px;">
															Año en Generación Códigos
														</th>
														<th align="center" style="padding:14px;font-weight:600;font-size:14px;width:180px;">
															Año en Proceso de Admisión
														</th>
													</tr>
													{filas_programas}
												</table>
											</td>
										</tr>
										<!-- Instrucciones -->
										
										<!-- Footer -->
										<tr>
											<td style="padding:20px 25px;background:#f8f9fa;border-top:1px solid #e8e8e8;">
												<p style="margin:0;color:#6b7a90;font-size:12px;line-height:1.6;">
													<strong>🤖 Notificación automática</strong> del RPA de Matrícula CENTRUM<br>
													Fecha: <strong>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</strong><br>
													<span style="color:#999;">
														Este reporte se genera cuando se detectan años incorrectos durante el proceso de validación.
													</span>
												</p>
											</td>
										</tr>
									</table>
								</td>
							</tr>
						</table>
					</body>
				</html>
			"""

			msg.attach(MIMEText(html, 'html'))
			toaddrs = emails + cc + bcc
			
			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			server.sendmail(from_address, toaddrs, msg.as_string())
			server.quit()
			
			print(f"[RPA][MAIL] ✅ Correo enviado: {total_programas} programa(s) con año incorrecto")
			return True
		except Exception as e:
			print(f"[RPA][WARN] ❌ No se pudo enviar correo de Validación de años: {e}")
			import traceback
			traceback.print_exc()
			return False
		

	def enviarCorreoAlumnosSinCodigo(self, nombre_programa, alumnos_sin_codigo):
		"""
		Envía correo notificando alumnos sin código de alumno generado.
		nombre_programa: nombre del proceso/programa.
		alumnos_sin_codigo: lista de dicts con keys:
		    CANDIDATO, NUMERO DOCUMENTO, ESTADO POSTULANTE,
		    GRUPO ADMISIÓN, CUMPLE REQUISITOS, DOCUMENTO REFRENDADO
		"""
		try:
			emails = [e.strip() for e in self.emailgencodigo.split(",")]
			cc = []
			bcc = []
			# Calcular totales
			subject = f"Alumnos por revisar para generación de código - {nombre_programa}"
			from_address = "RPA Matricula CENTRUM <noreply@centrummailing.pucp.edu.pe>"
			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)
			if cc:
				msg['Cc'] = ", ".join(cc)
			msg['Subject'] = subject

			

			filas_html = ''
			for alumno in alumnos_sin_codigo:
				filas_html += f"""
				<tr>
					<td style="border:1px solid #ccc; padding:6px;">{alumno['CANDIDATO']}</td>
					<td style="border:1px solid #ccc; padding:6px;">{alumno['NUMERO DOCUMENTO']}</td>
					<td style="border:1px solid #ccc; padding:6px;">{alumno['ESTADO POSTULANTE']}</td>
					<td style="border:1px solid #ccc; padding:6px;">{alumno['GRUPO ADMISIÓN']}</td>
					<td style="border:1px solid #ccc; padding:6px;">{alumno['CUMPLE REQUISITOS']}</td>
					<td style="border:1px solid #ccc; padding:6px;">{alumno['DOCUMENTO REFRENDADO']}</td>
				</tr>"""

			cuerpo_html = f"""
			<p>Se encontraron <strong>{len(alumnos_sin_codigo)}</strong> alumno(s) sin código generado
			en el proceso: <strong>{nombre_programa}</strong></p>
			<table style="border-collapse:collapse; font-family:Arial, sans-serif; font-size:13px;">
				<thead>
					<tr style="background-color:#003366; color:white;">
						<th style="border:1px solid #ccc; padding:6px;">CANDIDATO</th>
						<th style="border:1px solid #ccc; padding:6px;">NÚMERO DOCUMENTO</th>
						<th style="border:1px solid #ccc; padding:6px;">ESTADO POSTULANTE</th>
						<th style="border:1px solid #ccc; padding:6px;">GRUPO ADMISIÓN</th>
						<th style="border:1px solid #ccc; padding:6px;">CUMPLE REQUISITOS</th>
						<th style="border:1px solid #ccc; padding:6px;">DOCUMENTO REFRENDADO</th>
					</tr>
				</thead>
				<tbody>
					{filas_html}
				</tbody>
			</table>
			"""

			html = f"""
				<html>
					<body style="margin:0;padding:0;background:#f4f7fb;font-family:Arial,Helvetica,sans-serif;">
						<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f7fb;padding:20px 0;">
							<tr>
								<td align="center">
									<table width="750" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #d9e6f2;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
										<!-- Header -->
										<tr>
											<td style="background:#174275;color:#ffffff;padding:20px;text-align:center;">
												<h1 style="margin:0;font-size:22px;font-weight:600;">
													⚠️ Revisar Generacíón de Códigos
												</h1>
												<p style="margin:8px 0 0 0;font-size:14px;opacity:0.9;">
													Revisión requerida en Campus Virtual
												</p>
											</td>
										</tr>
										<tr>
											<td style="background:#174275;color:#ffffff;padding:20px;text-align:center;">
												
											</td>
										</tr>
										{cuerpo_html}
										
									</table>
								</td>
							</tr>
						</table>
					</body>
				</html>
			"""


			msg.attach(MIMEText(html, 'html'))
			toaddrs = emails + cc + bcc
			
			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			server.sendmail(from_address, toaddrs, msg.as_string())
			server.quit()
			
			
			return True
		except Exception as e:
			print(f"[RPA][WARN] ❌ No se pudo enviar correo de Validación de años: {e}")
			import traceback
			traceback.print_exc()
			return False
		
	
	
	def enviarCorreoDniCrm(self,programa, faltantes=None, crm_vacio=False):
		try:
			
			emails = [e.strip() for e in self.emaildnicrm.split(",") if e.strip()]
			cc = []
			bcc = []
			
			if crm_vacio:
				subject = f"⚠️ Importante: CRM sin datos para validación DNI - {programa['nombre_marketing']}"
				titulo = "&#9888; Importante: CRM sin datos para validación DNI"
				detalle_html = f"""
				<p>
					La consulta al CRM no devolvió registros para el programa:
				</p>

				<div style="background:#f4f8fc;border:1px solid #d9e6f2;
					border-radius:6px;padding:12px;margin:10px 0;">
					<strong>ID:</strong> {programa['id_programa']}<br>
					<strong>Proceso Admisión:</strong> {programa['nombre_proceso']}<br>
					<strong>Nombre Marketing:</strong> {programa['nombre_marketing']}<br>
					<strong>Nombre CISAM:</strong> {programa['nombre_cisam']}<br>
					<strong>CRM:</strong> {programa['codigo_crm']}<br>
				</div>

				<p>
					No fue posible validar los DNI del archivo de admisión.
				</p>
				"""
			else:
				subject = f"⚠️ Importante: N° Documentos no encontrados en CRM -  {programa['nombre_marketing']}"
				titulo = "&#9888; Importante: N° Documentos no encontrados en CRM"
				filas = ""

				for item in faltantes:
					filas += f"""
					<tr>
						<td style="padding:10px;">{item['dni']}</td>
						<td style="padding:10px;">{item['codigo_alumno']}</td>
						<td style="padding:10px;">{item['apellidos_nombres']}</td>
					</tr>
					"""

				detalle_html = f"""
				<p>
					Se detectaron <strong>N° Documentos del proceso de Admisión</strong>
					que no existen en la consulta del CRM para:
				</p>

				<div style="background:#f4f8fc;border:1px solid #d9e6f2;
					border-radius:6px;padding:12px;margin:10px 0;">
					<strong>ID:</strong> {programa['id_programa']}<br>
					<strong>Proceso Admisión:</strong> {programa['nombre_proceso']}<br>
					<strong>Nombre Marketing:</strong> {programa['nombre_marketing']}<br>
					<strong>Nombre CISAM:</strong> {programa['nombre_cisam']}<br>
					<strong>CRM:</strong> {programa['codigo_crm']}<br>
				</div>

				<p>
					Total de N° de Documentos no encontrados: <strong>{len(faltantes)}</strong>
				</p>
				"""

			from_address = "Plataforma-Centrum <noreply@centrummailing.pucp.edu.pe>"

			msg = MIMEMultipart()
			msg['From'] = from_address
			msg['To'] = ", ".join(emails)
			if cc:
				msg['Cc'] = ", ".join(cc)
			msg['Subject'] = subject

			tabla_html = ""

			if not crm_vacio:
				tabla_html = f"""
				<tr>
					<td style="padding:0 20px 20px;">
					<table width="100%" cellpadding="0" cellspacing="0"
						style="border:1px solid #d9e6f2;border-radius:6px;
						border-collapse:separate;overflow:hidden;">
						<tr style="background:#174275;color:#ffffff;">
						<th align="left" style="padding:10px;">N° Documento no encontrado</th>
						<th align="left" style="padding:10px;">Código alumno</th>
						<th align="left" style="padding:10px;">Apellidos y nombres</th>
						</tr>
						{filas}
					</table>
					</td>
				</tr>
				"""

			html = f"""
			<!DOCTYPE html>
			<html>
			<head>
			<meta charset="utf-8">
			<title>{titulo}</title>
			</head>
			<body>
			<table align="center" width="100%" cellpadding="0" cellspacing="0"
				style="background-color:#ffffff;font-family:Helvetica,Arial,sans-serif;">
				<tr>
				<td align="center">

					<table width="100%" cellpadding="0" cellspacing="0"
					style="background-image:url('https://centrumwebs.pucp.edu.pe/cisam/public/img/modulo/header_image.jpg');
					background-size:cover;background-position:center;padding:20px 0;">
					<tr>
						<td align="center">
						<img src="https://centrumwebs.pucp.edu.pe/cisam/public/img/login/logo-blanco.png"
							width="220" height="68" alt="CENTRUM PUCP"
							style="display:block;border:0;">
						</td>
					</tr>
					</table>

					<table width="600" cellpadding="0" cellspacing="0"
					style="background:#ffffff;margin-top:20px;border-collapse:collapse;">

					<tr>
						<td style="padding:20px;color:#174275;font-size:18px;">
						<strong>{titulo}</strong>
						</td>
					</tr>

					<tr>
						<td style="padding:0 20px 10px;color:#174275;font-size:15px;">
						<p>Estimados,</p>
						{detalle_html}
						</td>
					</tr>

					{tabla_html}

					<tr>
						<td style="padding:0 20px 20px;color:#174275;font-size:14px;">
						<p>
							Por favor, revisar la información y validar el caso.
						</p>
						<p style="color:#6b7a90;font-size:12px;">
							Mensaje generado automáticamente por el RPA de admisión.
						</p>
						</td>
					</tr>

					</table>

				</td>
				</tr>
			</table>
			</body>
			</html>
			"""


			msg.attach(MIMEText(html, 'html'))
			toaddrs = emails + cc + bcc
			
			server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
			server.starttls()
			server.login(self.smpt_user, self.smpt_pass)
			server.sendmail(from_address, toaddrs, msg.as_string())
			server.quit()

			print(f"[RPA][MAIL] Correo enviado validación DNI CRM: {programa['nombre_marketing']}")

		except Exception as e:
			print(f"[RPA][WARN] No se pudo enviar correo validación DNI CRM ({programa['nombre_marketing']}): {e}")
