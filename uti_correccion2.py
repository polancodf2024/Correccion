import streamlit as st
import sqlite3
import pandas as pd
import os

# Configuración de la base de datos
DB_FILE = os.path.join(os.path.dirname(__file__), "registro_correccion.sqlite")
PASSWORD = "Tt5plco5"

# Solicitar contraseña al inicio
input_password = st.text_input("Ingresa la contraseña para acceder:", type="password")

# Verificar la contraseña
if input_password != PASSWORD:
    st.error("Escribe la contraseña correcta, y presiona ENTER.")
    st.stop()

# Mostrar el logo del escudo
st.image("escudo_COLOR.jpg", width=150)

# Título de la aplicación
st.title("Gestión de Base de Datos: registro_correccion")

# Función para leer datos desde SQLite
def leer_datos_sqlite():
    try:
        conn = sqlite3.connect(DB_FILE)
        query = "SELECT * FROM registro_correccion"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al leer los datos: {e}")
        return pd.DataFrame()

# Función para reemplazar los datos en la base de datos
def reemplazar_datos_sqlite(df):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Eliminar los datos existentes
        cursor.execute("DELETE FROM registro_correccion")

        # Insertar los nuevos datos
        df.to_sql("registro_correccion", conn, if_exists="append", index=False)

        conn.commit()
        conn.close()
        st.success("Datos reemplazados exitosamente en la base de datos.")
    except Exception as e:
        st.error(f"Error al reemplazar los datos: {e}")

# Opción para subir el archivo de análisis
st.header("Subir los datos a la base de datos")
uploaded_csv = st.file_uploader("Selecciona un archivo CSV para cargar en la base de datos", type=["csv"])

if uploaded_csv is not None:
    try:
        # Leer el archivo subido
        df_nuevo = pd.read_csv(uploaded_csv)

        # Mostrar una vista previa del archivo subido
        st.subheader("Vista previa del archivo subido:")
        st.dataframe(df_nuevo)

        # Botón para reemplazar los datos
        if st.button("Reemplazar datos en la base de datos"):
            reemplazar_datos_sqlite(df_nuevo)
    except Exception as e:
        st.error("Error al procesar el archivo subido.")
        st.error(str(e))

# Opción para descargar los datos de la base de datos
st.header("Descargar los datos de la base de datos")
df_actual = leer_datos_sqlite()

if not df_actual.empty:
    try:
        # Botón para descargar los datos como CSV
        st.download_button(
            label="Descargar datos como CSV",
            data=df_actual.to_csv(index=False),
            file_name="registro_correccion.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error("Error al preparar los datos para descargar.")
        st.error(str(e))
else:
    st.warning("No hay datos disponibles en la base de datos.")

