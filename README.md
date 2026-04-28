# UserFinder
*Кочеткова Виктория Вячеславовна** 

## Описание
GUI-приложение для поиска пользователей GitHub с использованием официального GitHub API. Приложение позволяет:
1. Искать пользователей GitHub по имени
2. Просматривать детальную информацию о пользователе
3. Добавлять пользователей в избранное
4. Сохранять список избранных в JSON файл
5. Просматривать список избранных пользователей

## Технологии
1. Python 3.7+
2. Tkinter (GUI)
3. Requests (HTTP запросы)
4. JSON (хранение данных)

## Как использовать API

### GitHub REST API v3
Приложение использует следующие эндпоинты GitHub API:

#### 1. Поиск пользователей
GET https://api.github.com/search/users?q={query}&per_page=20

text
Параметры:
- `q` - поисковый запрос (логин пользователя)
- `per_page` - количество результатов на странице (макс. 100)

#### 2. Получение информации о пользователе
GET https://api.github.com/users/{username}

Установка и запуск
1. Клонирование репозитория
bash
git clone https://github.com/your-username/github-user-finder.git
cd github-user-finder
2. Установка зависимостей
bash
pip install -r requirements.txt
3. Запуск приложения
bash
python main.py

### Заголовки запросов
```python
headers = {
    "Accept": "application/vnd.github.v3+json"
}
