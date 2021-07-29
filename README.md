# Продуктовый помощник

# Описание
### Помощник предоставляющий пользователям возможность публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

# Использованные технологии
- Docker
- postresql
- nginx
- gunicorn
- python
- Django

# Инструкции по запуску
## Запуск контейнеров
- $: cd /Docker
- $: sudo docker-compose up

## Создание суперпользователя
- $: docker-compose exec backend python manage.py createsuperuser
### Или использовать пользователя admin@admin.ru:admin

# Тестовый сервер
![foodram workflow](https://github.com/KolesnikRV/foodgram-project-react/actions/workflows/foodram_workflow.yml/badge.svg?branch=master)

[Test Server](http://130.193.51.249/)

# Автор
## Студент яндекс практикум 12 когорта Роман Колесник