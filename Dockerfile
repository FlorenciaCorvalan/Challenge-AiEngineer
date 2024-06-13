# Usa una imagen de Python como base
FROM python:3.11-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido actual del directorio al contenedor en /app
COPY requirements.txt ./

# Instala las dependencias necesarias

RUN echo "Python version:" \
 && python --version \
 && echo "Pip version:" \
 && pip --version \
 && echo "Installing dependencies:" \
 && pip install -r requirements.txt \
 && echo "All installed Python packages:" \
 && pip freeze


COPY . ./

# Define el puerto en el que la aplicación va a escuchar
EXPOSE 5000

# Define el comando que se ejecutará al iniciar el contenedor
CMD ["python", "app.py"]