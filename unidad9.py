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

# Configuración de idioma con español como predeterminado
idioma = st.sidebar.selectbox("Idioma", ["Español", "English"], index=0)

# Configuración de correo
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "abcdf2024dfabc@gmail.com"
EMAIL_PASSWORD = "hjdd gqaw vvpj hbsy"  # Contraseña de aplicación
NOTIFICATION_EMAIL = "polanco@unam.mx"  # Correo para recibir los documentos
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
        "Servicios Solicitados": [", ".join(servicios)]
    }
    df = pd.DataFrame(data)

    if not Path(LOG_FILE).exists():
        df.to_excel(LOG_FILE, index=False)
    else:
        existing_df = pd.read_excel(LOG_FILE)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_excel(LOG_FILE, index=False)

# Función para enviar el correo de confirmación al usuario
def send_confirmation(email_usuario, nombre_usuario, servicios, idioma):
    mensaje = MIMEMultipart()
    mensaje['From'] = EMAIL_USER
    mensaje['To'] = email_usuario
    mensaje['Subject'] = "Confirmación de recepción de documento" if idioma == "Español" else "Document Receipt Confirmation"
    
    # Cuerpo del mensaje según el idioma
    if idioma == "Español":
        cuerpo = (f"Hola {nombre_usuario},\n\nHemos recibido tu documento y los siguientes servicios solicitados: "
                  f"{', '.join(servicios)}.\nGracias por enviarlo. En los próximos días te escribiremos.\n\n"
                  f"Atentamente,\nUnidad de Revisión de Artículos Científicos")
    else:
        cuerpo = (f"Hello {nombre_usuario},\n\nWe have received your document and the requested services are: "
                  f"{', '.join(servicios)}.\nThank you for submitting it. We will contact you in the following days.\n\n"
                  f"Sincerely,\nScientific Publications Review Center")
    
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

    cuerpo = f"Se ha recibido el documento adjunto y el registro de transacciones. Los servicios que solicita son: {', '.join(servicios)}."
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

# Contenido en español o inglés según el idioma seleccionado
if idioma == "Español":
    st.title("Unidad de Revisión de Artículos Científicos")
    nombre_completo = st.text_input("Nombre completo del autor")
    email = st.text_input("Correo electrónico del autor")
    email_confirmacion = st.text_input("Confirma tu correo electrónico")
    servicios_solicitados = st.multiselect(
        "¿Qué servicios solicita?",
        ["Verificación de originalidad", "Parafraseo", "Reporte de similitudes", "Revisión de estilo", "Traducción parcial", "Traducción total"]
    )
    st.error("El archivo que subirás no debe de incluir listado de autores, ni de adscripciones, ni figuras (pero sí los pies de figuras). El archivo no debe ser mayor a 20 MB.")
else:
    st.title("Scientific Publications Review Center")
    nombre_completo = st.text_input("Full name of the author")
    email = st.text_input("Author's email")
    email_confirmacion = st.text_input("Verify your email")
    servicios_solicitados = st.multiselect(
        "What services do you require?",
        ["Originality verification", "Paraphrasing", "Plagiarism report", "Style review"]
    )
    st.error("The file you upload should not include a list of authors, affiliations, or figures (but should include figure captions). The file size must not exceed 20 MB.")

# Subida de archivos
uploaded_file = st.file_uploader("Sube tu archivo .doc o .docx" if idioma == "Español" else "Upload your .doc or .docx file", type=["doc", "docx"])

# Verificación de condiciones y envío del archivo
if st.button("Enviar archivo" if idioma == "Español" else "Submit file"):
    if not nombre_completo:
        st.error("Por favor, ingresa tu nombre completo." if idioma == "Español" else "Please enter your full name.")
    elif not email or not email_confirmacion:
        st.error("Por favor, ingresa y confirma tu correo electrónico." if idioma == "Español" else "Please enter and confirm your email.")
    elif email != email_confirmacion:
        st.error("Los correos electrónicos no coinciden. Por favor, verifica." if idioma == "Español" else "The email addresses do not match. Please check.")
    elif uploaded_file is None:
        st.error("Por favor, adjunta un archivo .doc o .docx." if idioma == "Español" else "Please attach a .doc or .docx file.")
    elif len(uploaded_file.getbuffer()) > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"El archivo excede el tamaño máximo permitido de {MAX_FILE_SIZE_MB} MB." if idioma == "Español" else f"The file exceeds the maximum allowed size of {MAX_FILE_SIZE_MB} MB.")
    elif not servicios_solicitados:
        st.error("Por favor, selecciona al menos un servicio." if idioma == "Español" else "Please select at least one service.")
    else:
        # Mostrar mensaje de proceso en curso
        with st.spinner("Enviando archivo, por favor espera..." if idioma == "Español" else "Sending file, please wait..."):
            file_data = uploaded_file.getbuffer()
            file_name = uploaded_file.name

            # Guardar la transacción en el archivo Excel
            log_transaction(nombre_completo, email, file_name, servicios_solicitados)

            # Enviar correos
            send_confirmation(email, nombre_completo, servicios_solicitados, idioma)
            send_files_to_admin(file_data, file_name, servicios_solicitados)

            st.success("Archivo subido y correos enviados exitosamente." if idioma == "Español" else "File uploaded and emails sent successfully.")
            st.success("Gracias por usar este servicio, en breve recibirás una notificación en tu correo electrónico." if idioma == "Español" else "Thank you for using this service. You will receive a notification in your email shortly.")
            st.error("Cierra la aplicación" if idioma == "Español" else "Close the application")

            # Opcional: mostrar los servicios seleccionados en la confirmación
            st.write("Servicios solicitados:" if idioma == "Español" else "Requested services:", ", ".join(servicios_solicitados))

