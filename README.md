# praktikum_new_diplom

# Описание
Продуктовый помощник

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

# Автор
## Студент яндекс практикум 12 когорта Роман Колесник