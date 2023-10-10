# Фудграм - Социальная платформа для обмена рецептами

**Фудграм** - это веб-приложение, разработанное для обмена рецептами между пользователями. Здесь вы можете создавать, публиковать и находить интересные рецепты, добавлять их в избранное и подписываться на авторов. Также у вас есть возможность скачать список покупок для приготовления выбранных блюд.

## Функциональность

- Регистрация и аутентификация пользователей.
- Публикация и просмотр рецептов.
- Добавление рецептов в избранное.
- Добавление рецептов в список покупок.
- Подписка на авторов рецептов.
- Скачивание списка покупок.

## Технологический стек

- Фронтенд: HTML, CSS, JavaScript, React
- Бэкенд: Python, Django
- База данных: PostgreSQL
- Веб-сервер: Nginx
- Контейнеризация: Docker

## Локальное развертывание

1. Установите Docker на вашем компьютере.

2. Склонируйте репозиторий проекта:
   ```bash
   git clone https://github.com/slavajet/foodgram-project-react.git
3. Создайте файл `.env` в корневой папке проекта и укажите необходимые переменные окружения, например:

   ```env
   POSTGRES_DB=foodgramdb
   POSTGRES_USER=foodgramuser
   POSTGRES_PASSWORD=foodgrampassword
   DB_HOST=db
   DB_PORT=5432
   SECRET_KEY=ваш_секретный_ключ_здесь
   ALLOWED_HOSTS=ваш_домен_или_ip_здесь,localhost,127.0.0.1
   DEBUG=True
4. Запустите проект с помощью Docker Compose:

    ```bash
    docker-compose -f docker-compose.yml up -d
## Развертывание на сервере
1. Склонируйте на свой сервер файл docker-compose.prod.yml
2. Склонируйте с DockerHub контейнеры:
    ```bash
    docker pull slvajet/foodgram_backend
    docker pull slvajet/foodgram_frontend
    docker pull slvajet/foodgram_gateway
3. Cоздайте файл `.env` в корневой папке проекта и укажите необходимые переменные окружения, например:

   ```env
   POSTGRES_DB=foodgramdb
   POSTGRES_USER=foodgramuser
   POSTGRES_PASSWORD=foodgrampassword
   DB_HOST=db
   DB_PORT=5432
   SECRET_KEY=ваш_секретный_ключ_здесь
   ALLOWED_HOSTS=ваш_домен_или_ip_здесь,localhost,127.0.0.1
   DEBUG=True
4. Запустите проект с помощью Docker Compose в режиме Production:

    ```bash
    docker-compose -f docker-compose.prod.yml up -d

Проект разработан [Slava Jet](https://github.com/slavajet).

Связаться со мной: [тык](slavacaas@yandex.ru)