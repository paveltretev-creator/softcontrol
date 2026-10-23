=============
Софт контроль
=============

Описание проекта
================

Софт контроль — это десктопное приложение на Python/PyQt5 для управления
проектами в IT-компании. Приложение поддерживает четыре роли пользователей:

* **Администратор** — создаёт проекты, назначает руководителей и заказчиков,
  видит все проекты компании.
* **Руководитель (менеджер)** — управляет своими проектами, назначает
  разработчиков, редактирует описание и состав команды.
* **Заказчик** — видит свои проекты, общается в чате проекта.
* **Разработчик** — видит назначенные проекты, редактирует GitHub-ссылку,
  общается в чате.

Основные возможности
====================

* Авторизация пользователей по ролям
* Управление проектами (создание, редактирование, просмотр)
* Внутренний чат по каждому проекту
* Интеграция с GitHub (ссылки на репозитории)
* Хранение данных в SQLite

Структура проекта
=================

::

    softcontrol/
    ├── main.py                              # Точка входа, контроллер приложения
    ├── company_projects.db                  # База данных (создаётся автоматически)
    ├── data/
    │   ├── __init__.py
    │   └── database.py                      # Работа с SQLite
    ├── services/
    │   └── __init__.py                      # Бизнес-логика и утилиты
    └── ui/
        ├── __init__.py
        ├── windows/
        │   ├── __init__.py
        │   ├── login_window.py              # Окно авторизации
        │   ├── customer_window.py           # Кабинет заказчика
        │   ├── developer_window.py          # Кабинет разработчика
        │   ├── manager_window.py            # Кабинет руководителя
        │   └── admin_window.py              # Панель администратора
        └── dialogs/
            ├── __init__.py
            ├── create_project_dialog.py     # Диалог создания проекта
            ├── project_info_dialog.py       # Диалог информации о проекте
            ├── github_dialog.py             # Диалог ввода GitHub-ссылки
            └── edit_project_dialog.py       # Диалог редактирования проекта

API модулей
===========

Ниже приведена автоматическая документация, сгенерированная из docstrings
каждого модуля проекта.

.. toctree::
   :maxdepth: 2
   :caption: Модули проекта:

   main
   data.database
   services
   ui.windows.login_window
   ui.windows.customer_window
   ui.windows.developer_window
   ui.windows.manager_window
   ui.windows.admin_window
   ui.dialogs.create_project_dialog
   ui.dialogs.project_info_dialog
   ui.dialogs.github_dialog
   ui.dialogs.edit_project_dialog

Установка и запуск
==================

Установите зависимости::

    pip install PyQt5

Запустите приложение::

    python main.py

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
