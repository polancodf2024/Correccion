import streamlit as st
from pathlib import Path
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import sqlite3
from datetime import datetime
import pytz
import os

# Configuración
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "abcdf2024dfabc@gmail.com"
EMAIL_PASSWORD = "hjdd gqaw vvpj hbsy"
NOTIFICATION_EMAIL = "polanco@unam.mx"
DB_FILE = os.path.join(os.path.dirname(__file__), "registro_correccion.sqlite")

# Crear base de datos y tabla si no existen
def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registro_correccion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_hora TEXT NOT NULL,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL,
        numero_economico TEXT NOT NULL,
        file_name TEXT NOT NULL,
        servicios TEXT NOT NULL,
        estado TEXT DEFAULT 'Activo',
        fecha_terminacion TEXT
    )
    """)
    conn.commit()
    conn.close()

setup_database()

# Función para registrar en la base de datos
def guardar_registro_sqlite(nombre, email, numero_economico, file_name, servicios):
    tz_mexico = pytz.timezone("America/Mexico_City")
    fecha_hora = datetime.now(tz_mexico).strftime("%Y-%m-%d %H:%M:%S")
    servicios_str = ", ".join(servicios)

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO registro_correccion (fecha_hora, nombre, email, numero_economico, file_name, servicios)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (fecha_hora, nombre, email, numero_economico, file_name, servicios_str))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error al guardar el registro en la base de datos: {e}")

# Función para enviar notificación al administrador
def send_to_admin_with_files(user_file_data, user_file_name):
    try:
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_USER
        mensaje['To'] = NOTIFICATION_EMAIL
        mensaje['Subject'] = "Nuevo archivo recibido - Corrección de Estilo"

        cuerpo = "Se ha recibido un nuevo registro en el sistema. Consulta los archivos adjuntos."
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar el archivo del usuario
        part_user_file = MIMEBase("application", "octet-stream")
        part_user_file.set_payload(user_file_data)
        encoders.encode_base64(part_user_file)
        part_user_file.add_header("Content-Disposition", f"attachment; filename={user_file_name}")
        mensaje.attach(part_user_file)

        # Enviar correo
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, NOTIFICATION_EMAIL, mensaje.as_string())
    except Exception as e:
        st.error(f"Error al enviar notificación al administrador: {e}")

# Función para enviar confirmación al usuario
def send_confirmation(email, nombre, servicios, user_file_data, user_file_name):
    try:
        # Determinar el tipo MIME según la extensión del archivo
        mime_type = "application/vnd.ms-word" if user_file_name.endswith(".doc") else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_USER
        mensaje['To'] = email
        mensaje['Subject'] = "Confirmación de recepción"

        cuerpo = f"Hola {nombre}, hemos recibido tu archivo. Servicios solicitados: {', '.join(servicios)}."
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Configurar el archivo adjunto correctamente
        part_user_file = MIMEBase(*mime_type.split("/"))
        part_user_file.set_payload(user_file_data)
        encoders.encode_base64(part_user_file)
        part_user_file.add_header(
            "Content-Disposition",
            f"attachment; filename={user_file_name}"
        )
        mensaje.attach(part_user_file)

        # Enviar correo
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, email, mensaje.as_string())

        st.success("Correo de confirmación enviado al usuario.")
    except Exception as e:
        st.error(f"Error al enviar confirmación al usuario: {e}")


# Añadir logo y título
st.image("escudo_COLOR.jpg", width=100)
st.title("Corrección de Estilo")

# Solicitar información del usuario
nombre_completo = st.text_input("Nombre completo")
numero_economico = st.text_input("Número Económico")
email = st.text_input("Correo electrónico")
email_confirmacion = st.text_input("Confirma tu correo")

# Selección de servicios
opcion_otro = "Otro"
servicios_solicitados = st.multiselect(
    "¿Qué servicios de corrección solicita?",
    [opcion_otro, "Revisión de estilo", "Parafraseo", "Reporte de similitud", "Traducción parcial"]
)

# Campo adicional para "Otro" servicio
otro_servicio = None
if opcion_otro in servicios_solicitados:
    otro_servicio = st.text_input("Por favor, especifique el servicio si seleccionó 'Otro'.")

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu archivo (.doc, .docx)", type=["doc", "docx"])

# Procesar envío
if st.button("Enviar archivo"):
    if not nombre_completo or not numero_economico or not email or not email_confirmacion or email != email_confirmacion or uploaded_file is None:
        st.error("Por favor, completa todos los campos correctamente.")
    elif opcion_otro in servicios_solicitados and not otro_servicio:
        st.error("Por favor, especifica el servicio requerido.")
    else:
        with st.spinner("Enviando..."):
            file_data = uploaded_file.getbuffer()
            file_name = uploaded_file.name

            # Incluir el campo adicional si fue especificado
            if otro_servicio and otro_servicio.strip():
                servicios_solicitados.append(otro_servicio.strip())

            # Guardar en la base de datos SQLite
            guardar_registro_sqlite(nombre_completo, email, numero_economico, file_name, servicios_solicitados)

            # Enviar confirmación al usuario con el archivo adjunto
            send_confirmation(email, nombre_completo, servicios_solicitados, file_data, file_name)

            # Notificar al administrador con el archivo del usuario
            send_to_admin_with_files(file_data, file_name)

            st.success("Envío exitoso. Cierre la aplicación.")

