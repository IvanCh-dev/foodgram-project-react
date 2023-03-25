IP сервера 84.201.158.76
Superuser 
login: admin111
password: Admin111!

# Foodgram
### Описание
Сайт Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
### Технологии
Django Rest Framework
Python 3.7,
Django 2.2.16,
JWT,
Postgres 13.0
### Создание docker-compose и запуск проекта на сервере
 - 1) Клонировать репозиторий и перейти в него в командной строке
```bash
git clone git@github.com:IvanCh-dev/foodgram-project-react.git
```

 - 2) Отредактировать файл infra/docker-compose.yml,
 указав вместо image: ivanchdev/foodgram_frontend:latest свои данные doker hub

 - 3) В вашем резозитории github добавьте следующие Actions secrets and variables:

DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_NAME=<имя_вашей_бд>
DB_PORT=5432
DJANGO_SECRET_KEY=<секретный_ключ_jango_который_знает_разработчик_IvanCh-dev>
DOCKER_PASSWORD=<пароль_вашего_Docker_Hub>
DOCKER_USERNAME=<логин_вашего_Docker_Hub>
HOST=<ip_вашего_сервера>
PASSPHRASE=<если_есть_passphrase_к_ssh>
POSTGRES_DB=<имя_вашей_бд>
POSTGRES_PASSWORD=<пароль_пользователя_POSTGRES>
POSTGRES_USER=<имя_пользователя_POSTGRES>
SSH_KEY=<ваш_ssh_ключ>
USER=<логин_пользователя_имеющего_доступ_к_серверу>

 - 4) Скопиропать на сервер с локального ПК в домашнюю директорию пользователя, указанного в переменной USER:

```
scp infra/docker-compose.yml <логин_пользователя_имеющего_доступ_к_серверу>:<ip_вашего_сервера>:.
scp infra/nginx.conf <логин_пользователя_имеющего_доступ_к_серверу>:<ip_вашего_сервера>:.
```

 - 5) Зайдя на сервер по именем пользователя, указанного в переменной USER в домашнюю директорию:
```
touch .env
```
 - 6) Выполнить push в репозиторий github с локального пк

 - 7) После успешного завершения workflow на github выполнить миграции, собрать статику,
      загрузить список ингридиентов, создать superuser:
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py get_ingr_from_json
docker-compose exec backend python manage.py createsuperuser
```

Проект будет доступен по адресу http://<ip_вашего_сервера>/
Админ панель django будет доступна по адресу http://<ip_вашего_сервера>/admin/
Документация api будет доступна по адресу http://<ip_вашего_сервера>/docs/redoc.html
Api будет доступен по адресу http://<ip_вашего_сервера>/api/

Если потребуется удалить проект с сервера вместе с базой данных, можно выполнить на сервере следующее:

```
systemctl stop nginx
docker-compose stop
docker-compose rm
docker system prune -a --volumes
```

### Автор
https://github.com/IvanCh-dev
