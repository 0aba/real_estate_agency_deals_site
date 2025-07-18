# Описание
Сайт разрабатывался для курсового проекта по теме «Информационная система учета сделок агентства недвижимости».

## Содержание
1. [Требования для работы](#Требования-для-работы)
2. [Зависимости Python](#Зависисмости-Python)
3. [Структура .env файлов](#Структура-env-файлов)
4. [Docker](#Docker)

## Требования для работы
- **Python** ~=3.13.0
- **PostgreSQL** ~=17.2

## Зависимости Python
Все зависимости для Python написаны в `pyproject.toml`, для установки перейти в директорию к этому файлу и написать:
```sh
pip install -e .
```

## Структура .env файлов
Всего есть 2 файла .env, если `DEBUG=True`, то загружается `.env.dev`, иначе `.env.prod`.
Оба файла имеют следующую структура:
```env
# PostgreSQL
NAME_DB="exemple"
USER_DB="exemple"
PASSWORD_DB="exemple"
HOST_DB="127.0.0.1"                        # Default PostgreSQL
PORT_DB="5432"                             # Default PostgreSQL
# Email
EMAIL_HOST_USER="exemple@gmail.com"
EMAIL_HOST_PASSWORD="ffff ffff ffff ffff" 
# Server
MAIN_HOST='https://exemple-host.com'       # Optional (default 127.0.0.1:8000)
```

## Docker
Для сборки Docker-образа информационной системы относительно корневого каталога нужно написать:
```sh
docker build -t real-estate-agency-deals-site .
```
Далее для запуска самой информационной системы нужно воспользоваться `docker-compose.yaml`.
Но важно, что текущий `docker-compose.yaml` подходит только для запуска в режиме разработки и никак больше!
Так же при запуске Docker Compose нужно передать `env` файл.
Для запуска Docker Compose информационной системы, нужно сначала собрать Docker-образ информационной системы, далее относительно корневого каталога нужно написать:
```sh
docker compose --env-file .env.dev up
```

<pre>
---------------[meow]---------------
───▐▀▄──────▄▀▌───▄▄▄▄▄▄▄─────────── 
───▌▒▒▀▄▄▄▄▀▒▒▐▄▀▀▒██▒██▒▀▀▄──────── 
──▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▀▄────── 
──▌▒▒▒▒▒▒▒▒▒▒▒▒▒▄▒▒▒▒▒▒▒▒▒▒▒▒▒▀▄──── 
▀█▒▒█▌▒▒█▒▒▐█▒▒▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌─── 
▀▌▒▒▒▒▒▀▒▀▒▒▒▒▒▀▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐─▄▄ 
▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▄█▒█ 
▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▀──── 
──▐▄▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▄▌──── 
────▀▄▄▀▀▀▀▄▄▀▀▀▀▀▀▄▄▀▀▀▀▀▀▄▄▀────── 
</pre>
