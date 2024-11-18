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

# Configuración
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "abcdf2024dfabc@gmail.com"
EMAIL_PASSWORD = "hjdd gqaw vvpj hbsy"
NOTIFICATION_EMAIL = "polanco@unam.mx"
LOG_FILE = "registro_correccion.csv"

# Función para registrar transacciones en CSV
def log_transaction(nombre, email, file_name, servicios):
    tz_mexico = pytz.timezone("America/Mexico_City")
    fecha_hora = datetime.now(tz_mexico).strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "Nombre": [nombre],
        "Email": [email],
        "Fecha y Hora": [fecha_hora],  # Marca de tiempo
        "Nombre del Archivo": [file_name],
        "Servicios Solicitados": [", ".join(servicios)]
    }
    df = pd.DataFrame(data)

    if not Path(LOG_FILE).exists():
        df.to_csv(LOG_FILE, index=False)
    else:
        existing_df = pd.read_csv(LOG_FILE)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_csv(LOG_FILE, index=False)

# Función para enviar confirmación al usuario
def send_confirmation(email_usuario, nombre_usuario, servicios, idioma):
    mensaje = MIMEMultipart()
    mensaje['From'] = EMAIL_USER
    mensaje['To'] = email_usuario
    mensaje['Subject'] = "Confirmación de recepción de documento" if idioma == "Español" else "Document Receipt Confirmation"

    cuerpo = (
        f"Hola {nombre_usuario},\n\nHemos recibido tu documento y los siguientes servicios solicitados: "
        f"{', '.join(servicios)}.\nGracias por enviarlo." if idioma == "Español"
        else f"Hello {nombre_usuario},\n\nWe have received your document and the requested services are: "
             f"{', '.join(servicios)}.\nThank you for submitting it."
    )
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, email_usuario, mensaje.as_string())

# Función para enviar el archivo al administrador
def send_files_to_admin(file_data, file_name, servicios):
    mensaje = MIMEMultipart()
    mensaje['From'] = EMAIL_USER
    mensaje['To'] = NOTIFICATION_EMAIL
    mensaje['Subject'] = "Nuevo documento recibido"

    cuerpo = f"Se ha recibido el documento adjunto y el registro de transacciones. Los servicios solicitados son: {', '.join(servicios)}."
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    part = MIMEBase("application", "octet-stream")
    part.set_payload(file_data)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={file_name}")
    mensaje.attach(part)

    # Adjuntar el archivo de registro CSV
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

# Añadir el logo y el título
st.image("escudo_COLOR.jpg", width=100)
st.title("Revisión de Artículos Científicos")

# Solicitar información del usuario
nombre_completo = st.text_input("Nombre completo del autor")
email = st.text_input("Correo electrónico del autor")
email_confirmacion = st.text_input("Confirma tu correo electrónico")
numero_economico = st.text_input("Número económico del autor")

# Selección de servicios
servicios_solicitados = st.multiselect(
    "¿Qué servicios solicita?",
    ["Verificación de originalidad", "Parafraseo", "Reporte de similitudes", "Revisión de estilo", "Traducción parcial"]
)

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu archivo .doc o .docx", type=["doc", "docx"])

if st.button("Enviar archivo"):
    if not nombre_completo or not email or not email_confirmacion or email != email_confirmacion or not numero_economico or uploaded_file is None:
        st.error("Por favor, completa todos los campos correctamente.")
    else:
        with st.spinner("Enviando archivo, por favor espera..."):
            file_data = uploaded_file.getbuffer()
            file_name = uploaded_file.name

            log_transaction(nombre_completo, email, file_name, servicios_solicitados)

            send_confirmation(email, nombre_completo, servicios_solicitados, "Español")
            send_files_to_admin(file_data, file_name, servicios_solicitados)

            st.success("Archivo subido y correos enviados exitosamente.")

