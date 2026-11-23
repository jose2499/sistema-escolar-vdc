FROM python:3.11-slim

WORKDIR /app

# Capa 1: dependencias (se reutiliza mientras requirements.txt no cambie)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Capa 2: código fuente
COPY . .

# En el contenedor solo se ejecutan las pruebas de la lógica (la ventana corre en el PC)
CMD ["pytest"]
