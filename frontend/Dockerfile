FROM python:3.13

# устанавливаем рабочую директорию внутри контейнера как /app
WORKDIR /app

# копируем файл с зависимостями (requirements.txt) в текущую директорию контейнера (/app)
COPY requirements.txt .

# устанавливаем зависимости python без кэша для уменьшения размера образа
RUN pip install --no-cache-dir -r requirements.txt

# копируем весь исходный код приложения в рабочую директорию контейнера
COPY . .

# объявляем, что контейнер будет слушать порт 8501 (для streamlit)
EXPOSE 8501

# проверка здоровья контейнера: отправляем запрос на health-check эндпоинт streamlit
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# команда запуска приложения: запускаем streamlit с указанием порта и адреса
ENTRYPOINT ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]