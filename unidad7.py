import streamlit as st
from pathlib import Path
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from datetime import datetime
import pytz

# Configuración de correo
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "abcdf2024dfabc@gmail.com"
EMAIL_PASSWORD = "hjdd gqaw vvpj hbsy"  # Contraseña de aplicación
NOTIFICATION_EMAIL = "cpg7000cpg@gmail.com"  # Correo para recibir los documentos
LOG_FILE = "transaction_log.xlsx"
MAX_FILE_SIZE_MB = 20  # Tamaño máximo permitido en MB

# Función para guardar la transacción en el archivo Excel
def log_transaction(nombre, email, file_name, servicios):
    tz_mexico = pytz.timezone("America/Mexico_City")
    fecha_hora = datetime.now(tz_mexico).strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "Nombre": [nombre],
        "Email": [email],
        "Fecha y Hora": [fecha_hora],
        "Nombre del Archivo": [file_name],
        "Servicios Solicitados": [", ".join(servicios)]  # Añadir los servicios seleccionados
    }
    df = pd.DataFrame(data)

    if not Path(LOG_FILE).exists():
        df.to_excel(LOG_FILE, index=False)
    else:
        existing_df = pd.read_excel(LOG_FILE)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_excel(LOG_FILE, index=False)

# Función para enviar el correo de confirmación al usuario
def send_confirmation(email_usuario, nombre_usuario, servicios):
    mensaje = MIMEMultipart()
    mensaje['From'] = EMAIL_USER
    mensaje['To'] = email_usuario
    mensaje['Subject'] = "Confirmación de recepción de documento"
    cuerpo = f"Hola {nombre_usuario},\n\nHemos recibido tu documento y solicitado los siguientes servicios: {', '.join(servicios)}.\nGracias por enviarlo. En los próximos días te escribiremos.\n\nAtentamente,\nUnidad de Revisión de Artículos Científicos"
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, email_usuario, mensaje.as_string())

# Función para enviar el archivo y el registro a la unidad
def send_files_to_admin(file_data, file_name, servicios):
    mensaje = MIMEMultipart()
    mensaje['From'] = EMAIL_USER
    mensaje['To'] = NOTIFICATION_EMAIL
    mensaje['Subject'] = "Nuevo documento recibido"

    cuerpo = f"Se ha recibido un nuevo documento adjunto y el registro de transacciones. Los servicios solicitados son: {', '.join(servicios)}."
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Adjuntar archivo subido
    part = MIMEBase("application", "octet-stream")
    part.set_payload(file_data)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={file_name}")
    mensaje.attach(part)

    # Adjuntar archivo de log
    with open(LOG_FILE, "rb") as f:
        log_part = MIMEBase("application", "octet-stream")
        log_part.set_payload(f.read())
        encoders.encode_base64(log_part)
        log_part.add_header("Content-Disposition", f"attachment; filename={LOG_FILE}")
        mensaje.attach(log_part)

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, NOTIFICATION_EMAIL, mensaje.as_string())

# Añadir el logo y el título de la página
st.image("escudo_COLOR.jpg", width=100)
# Configuración de la interfaz de Streamlit
st.title("Unidad de Revisión de Artículos Científicos")
nombre_completo = st.text_input("Nombre completo del autor")
email = st.text_input("Correo electrónico del autor")
email_confirmacion = st.text_input("Confirma tu correo electrónico")

# Pregunta de servicios solicitados
servicios_solicitados = st.multiselect(
    "¿Qué servicios solicita?",
    ["Verificación de originalidad", "Parafraseo", "Reporte de plagio", "Revisión de estilo", "Traduccción parcial", "Traducción total"]
)

# Mensaje adicional para el usuario
st.error("El archivo que subirás no debe de incluir listado de autores, ni de adscripciones, ni figuras (pero si los pies de figuras). El archivo no debe ser mayor a 20 MB.")

# Subida de archivos
uploaded_file = st.file_uploader("Sube tu archivo .doc o .docx", type=["doc", "docx"])

if st.button("Enviar archivo"):
    if not nombre_completo:
        st.error("Por favor, ingresa tu nombre completo.")
    elif not email or not email_confirmacion:
        st.error("Por favor, ingresa y confirma tu correo electrónico.")
    elif email != email_confirmacion:
        st.error("Los correos electrónicos no coinciden. Por favor, verifica.")
    elif uploaded_file is None:
        st.error("Por favor, adjunta un archivo .doc o .docx.")
    elif len(uploaded_file.getbuffer()) > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"El archivo excede el tamaño máximo permitido de {MAX_FILE_SIZE_MB} MB.")
    elif not servicios_solicitados:
        st.error("Por favor, selecciona al menos un servicio.")
    else:
        # Mostrar mensaje de proceso en curso
        with st.spinner("Enviando archivo, por favor espera..."):
            file_data = uploaded_file.getbuffer()
            file_name = uploaded_file.name

            # Guardar la transacción en el archivo Excel
            log_transaction(nombre_completo, email, file_name, servicios_solicitados)

            # Enviar correos
            send_confirmation(email, nombre_completo, servicios_solicitados)
            send_files_to_admin(file_data, file_name, servicios_solicitados)

            st.success("Archivo subido y correos enviados exitosamente.")
            st.success("Gracias por usar este servicio, en breve recibirás una notificación en tu correo electrónico.")
            st.error ("Cierra la aplicación")

            # Opcional: mostrar los servicios seleccionados en la confirmación
            st.write("Servicios solicitados:", ", ".join(servicios_solicitados))

