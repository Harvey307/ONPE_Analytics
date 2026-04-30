# Usamos una imagen ligera de Python
FROM python:3.9-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Instalamos las librerías necesarias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos tu app y el CSV a la imagen
COPY . .

# Exponemos el puerto de Streamlit
EXPOSE 8501

# Comando para arrancar la web
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]