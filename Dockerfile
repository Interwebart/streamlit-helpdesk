# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Указываем порт, который будет использовать Streamlit
EXPOSE 8501

# Команда для запуска приложения
CMD ["streamlit", "run", "Helpdesk.py", "--server.port=8501", "--server.address=0.0.0.0"]