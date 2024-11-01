import streamlit as st
import zipfile
import os
from pathlib import Path

# Ruta de la carpeta uploads
upload_folder = Path("uploads")

# Verificar si la carpeta existe y contiene archivos
if upload_folder.exists() and any(upload_folder.iterdir()):
    # Listar archivos en uploads
    st.write("Archivos en la carpeta 'uploads':")
    for file in upload_folder.iterdir():
        st.write(file.name)

    # Crear un archivo ZIP con todo el contenido de 'uploads'
    zip_path = upload_folder / "uploads_contenido.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in upload_folder.iterdir():
            zipf.write(file, file.name)

    # Botón para descargar el archivo ZIP
    with open(zip_path, "rb") as f:
        st.download_button(
            label="Descargar todo el contenido de 'uploads' en ZIP",
            data=f,
            file_name="uploads_contenido.zip",
            mime="application/zip"
        )
else:
    st.write("La carpeta 'uploads' está vacía o no existe.")

