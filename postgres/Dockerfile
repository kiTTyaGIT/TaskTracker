FROM postgres:17

# Копируем init.sql из той же папки
COPY init.sql /docker-entrypoint-initdb.d/init.sql

# Даем права
RUN chmod +r /docker-entrypoint-initdb.d/init.sql