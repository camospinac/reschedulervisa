from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import sys

usuario = 'correo@correo.com'
contrasena = 'contraseña'
cedula = 'cedula'
año_parametro = 'xxxx'

def finalizar():
    with open('estado_hecho.txt', 'w') as f:
        f.write('Finalizado')

def enviar_correo(fecha_disponible):
    remitente = "correo@correo.com"
    destinatario = "correo@correo.com"
    asunto = "Notificación - Agendamiento de Turno"
    cuerpo = f"Se ha encontrado una fecha disponible para la cita: {fecha_disponible}."
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))
    try:
        servidor = smtplib.SMTP("smtp-mail.outlook.com", 587)
        servidor.starttls()
        servidor.login(remitente, "contraseña_email")
        servidor.sendmail(remitente, destinatario, mensaje.as_string())
        servidor.quit()
        print(f"Correo enviado con éxito a {destinatario}.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

try:
    # Configuración del navegador y opciones de Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options=options)

    # Lógica principal del script de Selenium
    driver.get("https://ais.usvisa-info.com/es-co/niv/users/sign_in")
    user_input = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'user_email')))
    password_input = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'user_password')))
    checkbox = driver.find_element(By.ID, "policy_confirmed")
    driver.execute_script("arguments[0].click();", checkbox)
    user_input.send_keys(usuario)
    password_input.send_keys(contrasena)
    password_input.send_keys(Keys.ENTER)
    time.sleep(5)
    
    # Navegación y búsqueda de fechas disponibles
    driver.get(f"https://ais.usvisa-info.com/es-co/niv/schedule/{cedula}/appointment")
    time.sleep(3)
    fecha_clic = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "appointments_consulate_appointment_date")))
    fecha_clic.click() 
    fechas_disponibles = []
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-calendar")))

    while not fechas_disponibles:
        all_days = driver.find_elements(By.CSS_SELECTOR, ".ui-datepicker-calendar td[data-handler='selectDay']")
        if all_days:
            fechas_disponibles.extend(all_days)
        else:
            driver.execute_script("document.querySelector('.ui-datepicker-next').click();")
            month_year_text = driver.find_element(By.CLASS_NAME, "ui-datepicker-title").text
            _, year = month_year_text.split()
        
        if año_parametro and int(year) > int(año_parametro):
            print(f"Se ha alcanzado el año {year} sin encontrar fechas disponibles hasta el año {año_parametro}.")
            driver.quit()
            sys.exit()
        
        if fechas_disponibles:
            first_available_date = fechas_disponibles[0].find_element(By.TAG_NAME, "a")
            day_text = first_available_date.text
            month, year = month_year_text.split()
            month_number = datetime.strptime(month, "%B").month
            formatted_date = f"{day_text}-{month_number}-{year}"
            print(f"La fecha más cercana o habilitada encontrada es: {formatted_date}")
            first_available_date.click()
            break

    if fechas_disponibles:
        time.sleep(25)
        WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "appointments_consulate_appointment_time")))
        select_element = Select(driver.find_element(By.ID, "appointments_consulate_appointment_time"))  
        if len(select_element.options) > 1:
            select_element.select_by_index(1)
            print("Primera hora seleccionada: ", select_element.first_selected_option.text)
            fecha_clic_cas = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "appointments_asc_appointment_date")))
            fecha_clic_cas.click() 
            fechas_disponibles_cas = []
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-calendar")))
            while not fechas_disponibles_cas:
                all_days_cas = driver.find_elements(By.CSS_SELECTOR, ".ui-datepicker-calendar td[data-handler='selectDay']")
                if all_days_cas:
                    fechas_disponibles_cas.extend(all_days_cas)
                else:
                    driver.execute_script("document.querySelector('.ui-datepicker-next').click();")
                
                if fechas_disponibles_cas:
                    first_available_date_cas = fechas_disponibles_cas[0].find_element(By.TAG_NAME, "a")
                    driver.execute_script("arguments[0].click();", first_available_date_cas)
                    break
        else:
            print("No hay horas disponibles para seleccionar.")

    if fechas_disponibles_cas:
        time.sleep(25)
        WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "appointments_asc_appointment_time")))
        select_element_cas = Select(driver.find_element(By.ID, "appointments_asc_appointment_time"))
        if len(select_element_cas.options) > 1:
            select_element_cas.select_by_index(1)
        time.sleep(2)
        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "appointments_submit")))
        submit_button.click()
    enviar_correo(formatted_date)
    time.sleep(2)
    driver.quit()
    finalizar()
    sys.exit()

except Exception as e:
    print(f"Error inesperado")
    driver.quit()
    sys.exit()
