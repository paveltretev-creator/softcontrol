"""
Скрипт для генерации документации проекта «Софт контроль» с помощью Sphinx.

Создаёт структуру папки docs/, настраивает Sphinx, генерирует
rst-файлы для всех модулей и создаёт README.rst в корне проекта.

Использование:
    pip install sphinx
    python setup_docs.py
    cd docs
    make html   (или sphinx-build -b html . _build)
"""
import os
import subprocess
import sys


# Список модулей проекта для документации
PROJECT_MODULES = [
    'main',
    'database',
    'login_window',
    'customer_window',
    'developer_window',
    'manager_window',
    'admin_window',
    'create_project_dialog',
    'project_info_dialog',
    'github_dialog',
]

PROJECT_NAME = 'Софт контроль'
PROJECT_AUTHOR = 'Команда разработки'
PROJECT_VERSION = '1.0'


def check_sphinx():
    """Проверяет, установлен ли Sphinx."""
    try:
        import sphinx  # noqa: F401
        return True
    except ImportError:
        print("❌ Sphinx не установлен. Установите командой:")
        print("   pip install sphinx")
        return False


def create_docs_dir():
    """Создаёт папку docs/ для документации."""
    os.makedirs('docs', exist_ok=True)
    os.makedirs('docs/_static', exist_ok=True)
    os.makedirs('docs/_templates', exist_ok=True)
    print("✅ Папка docs/ создана")


def create_conf_py():
    """Создаёт файл конфигурации Sphinx — docs/conf.py."""
    conf_content = """# Configuration file for the Sphinx documentation builder.
# Автоматически сгенерировано скриптом setup_docs.py

import os
import sys
# Добавляем корень проекта в путь, чтобы autodoc нашёл модули
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = '{PROJECT_NAME}'
copyright = '2026, {PROJECT_AUTHOR}'
author = '{PROJECT_AUTHOR}'
version = '{PROJECT_VERSION}'
release = '{PROJECT_VERSION}'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',        # автогенерация из docstrings
    'sphinx.ext.viewcode',       # ссылки на исходный код
    'sphinx.ext.napoleon',       # поддержка Google/NumPy-стиля docstrings
    'sphinx.ext.autosummary',    # краткие сводки модулей
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'ru'

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']
html_title = '{PROJECT_NAME}'

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {{
    'members': True,
    'member-order': 'bysource',
    'undoc-members': False,
    'show-inheritance': True,
}}
autodoc_mock_imports = ['PyQt5']  # чтобы не требовать PyQt5 при сборке
""".format(PROJECT_NAME=PROJECT_NAME, PROJECT_AUTHOR=PROJECT_AUTHOR,
           PROJECT_VERSION=PROJECT_VERSION)
    with open('docs/conf.py', 'w', encoding='utf-8') as f:
        f.write(conf_content)
    print("✅ docs/conf.py создан")


def create_index_rst():
    """Создаёт главный файл документации — docs/index.rst."""
    modules_toctree = '\n   '.join(PROJECT_MODULES)
    # Вычисляем заголовок заранее
    title_line = '=' * len(PROJECT_NAME)
    
    index_content = """{title_line}
{PROJECT_NAME}
{title_line}

Описание проекта
----------------

**{PROJECT_NAME}** — это десктопное приложение на Python/PyQt5 для управления
проектами в IT-компании. Приложение поддерживает четыре роли пользователей:

* **Администратор** — создаёт проекты, назначает руководителей и заказчиков,
  видит все проекты компании.
* **Руководитель (менеджер)** — управляет своими проектами, назначает
  разработчиков, редактирует описание и состав команды.
* **Заказчик** — видит свои проекты, общается в чате проекта.
* **Разработчик** — видит назначенные проекты, редактирует GitHub-ссылку,
  общается в чате.

Основные возможности
--------------------

* Авторизация пользователей по ролям
* Управление проектами (создание, редактирование, просмотр)
* Внутренний чат по каждому проекту
* Интеграция с GitHub (ссылки на репозитории)
* Хранение данных в SQLite

Структура проекта
-----------------

* ``main.py`` — точка входа, контроллер приложения
* ``database.py`` — работа с базой данных SQLite
* ``login_window.py`` — окно авторизации
* ``customer_window.py`` — кабинет заказчика
* ``developer_window.py`` — кабинет разработчика
* ``manager_window.py`` — кабинет руководителя
* ``admin_window.py`` — панель администратора
* ``create_project_dialog.py`` — диалог создания проекта
* ``project_info_dialog.py`` — диалог информации о проекте
* ``github_dialog.py`` — диалог ввода GitHub-ссылки

API модулей
-----------

Ниже приведена автоматическая документация, сгенерированная из docstrings
каждого модуля проекта.

.. toctree::
   :maxdepth: 2
   :caption: Модули проекта:

   {modules_toctree}

Установка и запуск
------------------

1. Установите зависимости::

       pip install PyQt5

2. Запустите приложение::

       python main.py

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
""".format(PROJECT_NAME=PROJECT_NAME, modules_toctree=modules_toctree, 
           title_line=title_line)
    with open('docs/index.rst', 'w', encoding='utf-8') as f:
        f.write(index_content)
    print("✅ docs/index.rst создан")


def create_module_rst_files():
    """Создаёт rst-файлы для каждого модуля с директивой automodule."""
    for module in PROJECT_MODULES:
        # Вычисляем заголовок заранее
        title_line = '=' * (len(module) + 13)
        
        content = """Модуль ``{module}``
{title_line}

.. automodule:: {module}
   :members:
   :undoc-members:
   :show-inheritance:
""".format(module=module, title_line=title_line)
        filename = 'docs/{}.rst'.format(module)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    print("✅ Создано rst-файлов для {} модулей".format(len(PROJECT_MODULES)))


def create_makefile():
    """Создаёт Makefile для удобной сборки документации (Linux/Mac)."""
    makefile_content = """# Makefile for Sphinx documentation
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

help:
\t@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

.PHONY: help Makefile

%: Makefile
\t@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
"""
    with open('docs/Makefile', 'w', encoding='utf-8') as f:
        f.write(makefile_content)
    print("✅ docs/Makefile создан")


def create_make_bat():
    """Создаёт make.bat для удобной сборки документации (Windows)."""
    bat_content = """@ECHO OFF
pushd %~dp0
set SPHINXBUILD=sphinx-build
set SOURCEDIR=.
set BUILDDIR=_build
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end
:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
:end
popd
"""
    with open('docs/make.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    print("✅ docs/make.bat создан")


def create_readme_rst():
    """Создаёт README.rst в корне проекта (в формате reStructuredText)."""
    title_line = '=' * len(PROJECT_NAME)
    readme_content = """{title_line}
{PROJECT_NAME}
{title_line}

.. image:: https://img.shields.io/badge/python-3.8%2B-blue
   :alt: Python 3.8+
.. image:: https://img.shields.io/badge/license-MIT-green
   :alt: License

Описание
--------

**{PROJECT_NAME}** — десктопное приложение для управления проектами в IT-компании,
написанное на Python с использованием библиотеки PyQt5. Данные хранятся в
локальной базе SQLite.

Приложение поддерживает четыре роли пользователей с разными правами:

* 🔐 **Администратор** — создаёт проекты, назначает руководителей и заказчиков
* 👔 **Руководитель** — управляет проектами и командой разработчиков
* 💼 **Заказчик** — просматривает свои проекты и общается в чате
* 💻 **Разработчик** — работает над проектами, ведёт GitHub-репозиторий

Возможности
-----------

✅ Авторизация пользователей с разделением по ролям

✅ Управление проектами: создание, редактирование, просмотр

✅ Внутренний чат для каждого проекта между участниками

✅ Интеграция с GitHub — хранение ссылок на репозитории

✅ Хранение данных в локальной SQLite-базе

✅ Интуитивный графический интерфейс на PyQt5

Структура проекта
-----------------

::

    soft_control/
    ├── main.py                    # Точка входа, контроллер приложения
    ├── database.py                # Работа с SQLite
    ├── login_window.py            # Окно авторизации
    ├── customer_window.py         # Кабинет заказчика
    ├── developer_window.py        # Кабинет разработчика
    ├── manager_window.py          # Кабинет руководителя
    ├── admin_window.py            # Панель администратора
    ├── create_project_dialog.py   # Диалог создания проекта
    ├── project_info_dialog.py     # Диалог информации о проекте
    ├── github_dialog.py           # Диалог ввода GitHub-ссылки
    ├── edit_project_dialog.py     # Диалог редактирования проекта
    ├── company_projects.db        # База данных (создаётся автоматически)
    ├── docs/                      # Документация Sphinx
    └── README.rst                 # Этот файл

Установка
---------

1. Клонируйте репозиторий::

       git clone <url-репозитория>
       cd soft_control

2. Установите зависимости::

       pip install PyQt5

3. Запустите приложение::

       python main.py

При первом запуске автоматически создастся база данных ``company_projects.db``.

Сборка документации
-------------------

Документация генерируется с помощью `Sphinx <https://www.sphinx-doc.org/>`_.

1. Установите Sphinx::

       pip install sphinx

2. Сгенерируйте структуру документации::

       python setup_docs.py

3. Соберите HTML-документацию::

       cd docs
       make html          # Linux/Mac
       make.bat html      # Windows

4. Откройте ``docs/_build/html/index.html`` в браузере.

Требования
----------

* Python 3.8+
* PyQt5
* SQLite (встроен в Python)

Лицензия
--------

MIT License

Контакты
--------

По всем вопросам обращайтесь к команде разработки.

----

*Документация сгенерирована с помощью Sphinx*
""".format(title_line=title_line, PROJECT_NAME=PROJECT_NAME)
    with open('README.rst', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ README.rst создан в корне проекта")


def create_readme_md():
    """Создаёт также README.md для GitHub (Markdown-версия)."""
    # Используем конкатенацию строк, чтобы избежать проблем с тройными кавычками
    code_block_start = '```'
    readme_md = (
        "# {PROJECT_NAME}\n\n"
        "Десктопное приложение для управления проектами в IT-компании на Python/PyQt5.\n\n"
        "## Описание\n\n"
        "**{PROJECT_NAME}** поддерживает четыре роли пользователей:\n\n"
        "- 🔐 **Администратор** — создаёт проекты, назначает руководителей и заказчиков\n"
        "- 👔 **Руководитель** — управляет проектами и командой разработчиков\n"
        "- 💼 **Заказчик** — просматривает свои проекты и общается в чате\n"
        "- 💻 **Разработчик** — работает над проектами, ведёт GitHub-репозиторий\n\n"
        "## Возможности\n\n"
        "- ✅ Авторизация пользователей с разделением по ролям\n"
        "- ✅ Управление проектами: создание, редактирование, просмотр\n"
        "- ✅ Внутренний чат для каждого проекта между участниками\n"
        "- ✅ Интеграция с GitHub — хранение ссылок на репозитории\n"
        "- ✅ Хранение данных в локальной SQLite-базе\n"
        "- ✅ Интуитивный графический интерфейс на PyQt5\n\n"
        "## Установка\n\n"
        "{code_block_start}bash\n"
        "pip install PyQt5\n"
        "python main.py\n"
        "{code_block_start}\n\n"
        "## Документация\n\n"
        "Полная документация (включая API модулей) генерируется через Sphinx:\n\n"
        "{code_block_start}bash\n"
        "pip install sphinx\n"
        "python setup_docs.py\n"
        "cd docs\n"
        "make html       # Linux/Mac\n"
        "make.bat html   # Windows\n"
        "{code_block_start}\n\n"
        "Откройте `docs/_build/html/index.html` в браузере.\n\n"
        "## Структура проекта\n\n"
        "{code_block_start}\n"
        "soft_control/\n"
        "├── main.py                    # Точка входа\n"
        "├── database.py                # Работа с SQLite\n"
        "├── login_window.py            # Окно авторизации\n"
        "├── customer_window.py         # Кабинет заказчика\n"
        "├── developer_window.py        # Кабинет разработчика\n"
        "├── manager_window.py          # Кабинет руководителя\n"
        "├── admin_window.py            # Панель администратора\n"
        "├── create_project_dialog.py   # Диалог создания проекта\n"
        "├── project_info_dialog.py     # Диалог информации о проекте\n"
        "├── github_dialog.py           # Диалог ввода GitHub-ссылки\n"
        "├── edit_project_dialog.py     # Диалог редактирования проекта\n"
        "└── docs/                      # Документация Sphinx\n"
        "{code_block_start}\n\n"
        "## Требования\n\n"
        "- Python 3.8+\n"
        "- PyQt5\n"
        "- SQLite (встроен в Python)\n\n"
        "## Лицензия\n\n"
        "MIT License\n"
    ).format(PROJECT_NAME=PROJECT_NAME, code_block_start=code_block_start)

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_md)
    print("✅ README.md создан в корне проекта (для GitHub)")


def build_docs():
    """Запускает сборку HTML-документации."""
    print("\n🔨 Запускаю сборку документации...")
    try:
        result = subprocess.run(
            ['sphinx-build', '-b', 'html', 'docs', 'docs/_build/html'],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print("✅ Документация успешно собрана!")
        print("📂 Откройте: docs/_build/html/index.html")
        return True
    except subprocess.CalledProcessError as e:
        print("⚠️  Ошибка сборки документации:\n{}".format(e.stderr))
        return False
    except FileNotFoundError:
        print("⚠️  sphinx-build не найден. Установите Sphinx: pip install sphinx")
        return False


def main():
    """Главная функция: создаёт всю структуру документации."""
    print("🚀 Генерация документации для проекта «{}»\n".format(PROJECT_NAME))

    if not check_sphinx():
        sys.exit(1)

    create_docs_dir()
    create_conf_py()
    create_index_rst()
    create_module_rst_files()
    create_makefile()
    create_make_bat()
    create_readme_rst()
    create_readme_md()

    print("\n" + "=" * 60)
    print("📚 Структура документации создана!")
    print("=" * 60)
    print("\nДалее вы можете:")
    print("  1. Собрать HTML-документацию: cd docs && make html")
    print("  2. Открыть README.rst или README.md в любом редакторе")
    print("  3. Загрузить README.md на GitHub — он отобразится автоматически")

    # Автоматически пытаемся собрать документацию
    reply = input("\nСобрать HTML-документацию сейчас? (y/n): ").strip().lower()
    if reply == 'y':
        build_docs()


if __name__ == '__main__':
    main()