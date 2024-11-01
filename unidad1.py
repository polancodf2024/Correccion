import streamlit as st
from pathlib import Path
import zipfile
import os
from itertools import chain
import pandas as pd
from datetime import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración inicial
UPLOAD_FOLDER = "uploads"
PASSWORD = "tt8plco8"
LOG_FILE = "transaction_log.xlsx"
NOTIFICATION_EMAIL = "cpg7000cpg@gmail.com"  # Correo al que se enviará la notificación

# Configuración de correo (ajusta estos valores con tus credenciales)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "abcdf2024dfabc@gmail.com"   # Reemplaza con el correo remitente
EMAIL_PASSWORD = "hjdd gqaw vvpj hbsy"    # Contraseña de aplicación

# Crear la carpeta de subida si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Añadir el logo y el título de la página
st.image("escudo_COLOR.jpg", width=100)
st.title("Unidad de Revisión de Artículos Científicos")
st.write("Por favor, proporciona tu nombre completo y correo electrónico para recibir notificaciones.")

# Solicitar el nombre completo y el correo electrónico del usuario (dos veces)
nombre_completo = st.text_input("Nombre completo del usuario")
email = st.text_input("Email del usuario")
email_confirmacion = st.text_input("Confirma tu Email")

# Subida de archivos
uploaded_file = st.file_uploader("Sube tu archivo .doc o .docx", type=["doc", "docx"])

# Nota informativa antes del botón de envío
st.write("**Nota:** El documento debe de ser .doc o .docx y no contener nombre o adscripción de los autores.")

# Función para guardar la transacción en el archivo Excel
def log_transaction(nombre, email, file_name):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "Nombre": [nombre],
        "Email": [email],
        "Fecha y Hora": [fecha_hora],
        "Nombre del Archivo": [file_name]
    }
    df = pd.DataFrame(data)

    # Si el archivo de log no existe, lo creamos con encabezados; si existe, añadimos una nueva fila
    if not os.path.exists(LOG_FILE):
        df.to_excel(LOG_FILE, index=False)
    else:
        existing_df = pd.read_excel(LOG_FILE)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_excel(LOG_FILE, index=False)

# Función para enviar el correo de notificación
def send_notification(email_usuario, nombre_usuario, file_name):
    mensaje = MIMEMultipart()
    mensaje['From'] = EMAIL_USER
    mensaje['To'] = NOTIFICATION_EMAIL
    mensaje['Subject'] = "Nuevo documento subido en la Unidad de Revisión de Artículos Científicos"
    
    # Cuerpo del correo
    cuerpo = f"""\
Hola,

Se ha subido un nuevo documento.

Nombre del usuario: {nombre_usuario}
Email del usuario: {email_usuario}
Nombre del archivo: {file_name}

Atentamente,

Unidad de Revisión de Artículos Científicos
"""
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Establecer conexión segura con el servidor SMTP
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, NOTIFICATION_EMAIL, mensaje.as_string())
        st.success("Correo de notificación enviado exitosamente.")
    except Exception as e:
        st.error(f"Error al enviar la notificación por correo: {e}")

# Botón de envío
if st.button("Enviar archivo"):
    # Validación de campos requeridos
    if not nombre_completo:
        st.error("Por favor, ingresa tu nombre completo.")
    elif not email or not email_confirmacion:
        st.error("Por favor, ingresa y confirma tu correo electrónico.")
    elif email != email_confirmacion:
        st.error("Los correos electrónicos no coinciden. Por favor, verifica.")
    elif uploaded_file is None:
        st.error("Por favor, adjunta un archivo .doc o .docx.")
    else:
        # Guardar el archivo si todas las condiciones se cumplen
        if uploaded_file.name.endswith((".doc", ".docx")):
            file_path = Path(UPLOAD_FOLDER) / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Archivo subido correctamente.")
            # Guardar la transacción en el archivo Excel, incluyendo el nombre del archivo subido
            log_transaction(nombre_completo, email, uploaded_file.name)
            # Enviar notificación de correo
            send_notification(email, nombre_completo, uploaded_file.name)
        else:
            st.error("Solo se permiten archivos con la extensión .doc o .docx.")

# Descargar archivos protegidos por contraseña
st.write("Área de Descarga (protegido por contraseña)")

password_input = st.text_input("Contraseña", type="password")
if st.button("Descargar archivos") and password_input == PASSWORD:
    # Crear un archivo zip con todos los archivos .doc, .docx y el archivo de log
    zip_path = Path(UPLOAD_FOLDER) / "archivos_subidos.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        # Usamos chain para iterar sobre ambos generadores
        for doc_file in chain(Path(UPLOAD_FOLDER).glob("*.doc"), Path(UPLOAD_FOLDER).glob("*.docx")):
            zipf.write(doc_file, doc_file.name)
        # Agregar el archivo de log
        if os.path.exists(LOG_FILE):
            zipf.write(LOG_FILE, LOG_FILE)
    
    # Ofrecer el archivo zip para descarga
    with open(zip_path, "rb") as f:
        st.download_button(
            label="Descargar archivos .doc y .docx junto con su registro",
            data=f,
            file_name="archivos_subidos.zip",
            mime="application/zip"
        )
else:
    if password_input:
        st.error("Contraseña incorrecta.")

# Limpiar archivos subidos
st.write("Recuerda limpiar el área de almacenamiento de archivos cuando sea necesario.")

