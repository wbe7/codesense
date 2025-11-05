# Используем официальный образ Python 3.13 в качестве базового
FROM python:3.11-slim

# Устанавливаем глобальную переменную окружения для отключения кэша pip
ENV PIP_NO_CACHE_DIR=1

# Устанавливаем системные зависимости, включая git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы с зависимостями
COPY requirements.txt .

# Устанавливаем pip-tools и синхронизируем окружение
RUN pip install pip-tools && \
    pip-sync requirements.txt

# Копируем исходный код и скрипты нашего проекта
COPY ./src /app/src
COPY ./scripts /app/scripts
COPY pyproject.toml .

# Устанавливаем наш проект в режиме редактирования
RUN pip install -e .

# По умолчанию ничего не запускаем, команда будет передана KFP
CMD ["/bin/bash"]
