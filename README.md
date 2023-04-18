## Проект «Yatube»

### Описание:

Yatube - социальная сеть для публикации дневников.

Повзоляет написание постов и публикации их в отдельных группах, подписки на посты, добавление и удаление записей и их комментирование. Подписки на любимых блогеров.

### Технологии:

Python 3.7

Django 3.2

SQLite


### Запуск проекта:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Guten-Edd/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python -3.7 -m venv env
```

```
source venv/Scripts/activate
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
cd yatube/
```

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Автор:
[Эдуард Соловьев](https://github.com/Guten-Edd)


<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" width="50" height="50"/>
