## hw05_final

# Социальная сеть блогеров

Социальная сеть для публикации личных дневников. Сайт, на котором можно создать свою страницу. Если на нее зайти, то можно посмотреть все записи автора. Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи. Автор может выбрать имя и уникальный адрес для своей страницы. Есть возможность модерировать записи и блокировать пользователей, если начнут присылать спам. Записи можно отправить в сообщество и посмотреть там записи разных авторов.

Python 3.9, Django 2.2 LTS, pytest 6.2.4
## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:ExpertNSK/hw05_final.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
