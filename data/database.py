"""
Модуль работы с базой данных SQLite (company_projects.db).

Содержит все функции для:
- аутентификации пользователей;
- получения списков проектов по ролям;
- создания и редактирования проектов;
- работы с чатом и GitHub-ссылками.
"""
import sqlite3
import datetime  # добавить в начало файла (к import sqlite3)

DB_NAME = 'company_projects.db'


def get_connection():
    """
    Создаёт и возвращает соединение с БД.

    Включает проверку внешних ключей (PRAGMA foreign_keys = ON).
    """
    conn = sqlite3.connect(DB_NAME)
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn


def authenticate_user(login: str, password: str):
    """
    Проверяет логин и пароль во всех таблицах пользователей.

    :param login: логин пользователя.
    :param password: пароль пользователя.
    :return: словарь {'id', 'fio', 'role'} или None, если не найден.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT id, fio, 'developer' AS role FROM developers WHERE login = ? AND password = ?
        UNION ALL
        SELECT id, fio, 'customer'  AS role FROM customers  WHERE login = ? AND password = ?
        UNION ALL
        SELECT id, fio, 'manager'   AS role FROM managers   WHERE login = ? AND password = ?
        UNION ALL
        SELECT id, fio, 'admin'     AS role FROM admins     WHERE login = ? AND password = ?
    '''
    cursor.execute(query, (login, password, login, password,
                           login, password, login, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {'id': result[0], 'fio': result[1], 'role': result[2]}
    return None


def get_customer_projects(customer_id: int):
    """
    Возвращает список проектов заказчика.

    :param customer_id: id заказчика.
    :return: список кортежей (id, name, description, manager_fio, deadline).
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT p.id, p.name, p.description, m.fio, p.deadline
        FROM projects p
        LEFT JOIN managers m ON p.manager_id = m.id
        WHERE p.customer_id = ?
    '''
    cursor.execute(query, (customer_id,))
    result = cursor.fetchall()
    conn.close()
    return result


def get_manager_projects(manager_id: int):
    """
    Возвращает список проектов руководителя вместе с ФИО разработчиков.

    :param manager_id: id руководителя.
    :return: список кортежей (id, name, description, deadline, developers_fio).
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT p.id, p.name, p.description, p.deadline,
               GROUP_CONCAT(d.fio, ', ')
        FROM projects p
        LEFT JOIN project_developers pd ON p.id = pd.project_id
        LEFT JOIN developers d ON pd.developer_id = d.id
        WHERE p.manager_id = ?
        GROUP BY p.id
    '''
    cursor.execute(query, (manager_id,))
    result = cursor.fetchall()
    conn.close()
    return result


def get_all_projects():
    """
    Возвращает список всех проектов (для администратора).

    :return: список кортежей (id, name, description, deadline,
                              manager_fio, customer_fio).
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT p.id, p.name, p.description, p.deadline,
               m.fio as manager_fio, c.fio as customer_fio
        FROM projects p
        LEFT JOIN managers m ON p.manager_id = m.id
        LEFT JOIN customers c ON p.customer_id = c.id
        ORDER BY p.id
    '''
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


def get_project_details(project_id: int):
    """
    Возвращает базовые детали проекта: название и описание.

    :param project_id: id проекта.
    :return: кортеж (name, description) или None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT name, description FROM projects WHERE id = ?',
        (project_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result


def get_all_developers():
    """
    Возвращает список всех разработчиков.

    :return: список кортежей (id, fio), отсортированных по ФИО.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, fio FROM developers ORDER BY fio')
    result = cursor.fetchall()
    conn.close()
    return result


def get_all_managers():
    """
    Возвращает список всех руководителей.

    :return: список кортежей (id, fio), отсортированных по ФИО.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, fio FROM managers ORDER BY fio')
    result = cursor.fetchall()
    conn.close()
    return result


def get_all_customers():
    """
    Возвращает список всех заказчиков.

    :return: список кортежей (id, fio), отсортированных по ФИО.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, fio FROM customers ORDER BY fio')
    result = cursor.fetchall()
    conn.close()
    return result


def get_project_developers(project_id: int):
    """
    Возвращает набор id разработчиков, назначенных на проект.

    :param project_id: id проекта.
    :return: set с id разработчиков.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT developer_id FROM project_developers WHERE project_id = ?',
        (project_id,)
    )
    result = {row[0] for row in cursor.fetchall()}
    conn.close()
    return result


def update_project_info(project_id: int, name: str, description: str):
    """
    Обновляет название и описание проекта.

    :param project_id: id проекта.
    :param name: новое название.
    :param description: новое описание.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE projects SET name = ?, description = ? WHERE id = ?',
        (name, description, project_id)
    )
    conn.commit()
    conn.close()


def set_project_developers(project_id: int, new_developer_ids: list):
    """
    Устанавливает новый состав разработчиков проекта.

    Пересчитывает добавленных/удалённых разработчиков и обновляет
    у них поле current_project_id.

    :param project_id: id проекта.
    :param new_developer_ids: список id разработчиков.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT developer_id FROM project_developers WHERE project_id = ?',
        (project_id,)
    )
    old_ids = {row[0] for row in cursor.fetchall()}
    new_ids = set(new_developer_ids)

    added = new_ids - old_ids
    removed = old_ids - new_ids

    cursor.execute('DELETE FROM project_developers WHERE project_id = ?',
                   (project_id,))
    for dev_id in new_ids:
        cursor.execute(
            'INSERT INTO project_developers (project_id, developer_id) VALUES (?, ?)',
            (project_id, dev_id)
        )
    for dev_id in added:
        cursor.execute(
            'UPDATE developers SET current_project_id = ? WHERE id = ?',
            (project_id, dev_id)
        )
    for dev_id in removed:
        cursor.execute(
            'UPDATE developers SET current_project_id = NULL WHERE id = ?',
            (dev_id,)
        )
    conn.commit()
    conn.close()


def set_project_manager_and_customer(project_id: int, manager_id: int, customer_id: int):
    """
    Назначает руководителю и заказчику проекта.

    :param project_id: id проекта.
    :param manager_id: id руководителя.
    :param customer_id: id заказчика.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE projects SET manager_id = ?, customer_id = ? WHERE id = ?',
        (manager_id, customer_id, project_id)
    )
    conn.commit()
    conn.close()


def get_developer_projects(developer_id: int):
    """
    Возвращает список проектов, в которых участвует разработчик.

    :param developer_id: id разработчика.
    :return: список кортежей (id, name, description, deadline, manager_fio).
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT p.id, p.name, p.description, p.deadline, m.fio
        FROM projects p
        LEFT JOIN managers m ON p.manager_id = m.id
        JOIN project_developers pd ON p.id = pd.project_id
        WHERE pd.developer_id = ?
    '''
    cursor.execute(query, (developer_id,))
    result = cursor.fetchall()
    conn.close()
    return result


def init_chat_table():
    """
    Создаёт таблицу chat_messages, если её ещё нет.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            sender_role TEXT NOT NULL,
            sender_fio TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()


def save_chat_message(project_id: int, sender_id: int, sender_role: str,
                      sender_fio: str, message: str):
    """
    Сохраняет сообщение в чат проекта.

    :param project_id: id проекта.
    :param sender_id: id отправителя.
    :param sender_role: роль отправителя.
    :param sender_fio: ФИО отправителя.
    :param message: текст сообщения.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_messages (project_id, sender_id, sender_role, sender_fio, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (project_id, sender_id, sender_role, sender_fio, message))
    conn.commit()
    conn.close()


def get_chat_messages(project_id: int):
    """
    Возвращает все сообщения чата проекта в хронологическом порядке.

    :param project_id: id проекта.
    :return: список кортежей (sender_fio, sender_role, message, timestamp).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sender_fio, sender_role, message, timestamp
        FROM chat_messages
        WHERE project_id = ?
        ORDER BY timestamp ASC
    ''', (project_id,))
    result = cursor.fetchall()
    conn.close()
    return result


def get_full_project_info(project_id: int):
    """
    Возвращает полную информацию о проекте в виде словаря.

    :param project_id: id проекта.
    :return: словарь с ключами name, description, deadline,
             github_url, manager_fio, customer_fio, developers
             или None, если проект не найден.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.name, p.description, p.deadline, p.github_url,
               m.fio as manager_fio, c.fio as customer_fio
        FROM projects p
        LEFT JOIN managers m ON p.manager_id = m.id
        LEFT JOIN customers c ON p.customer_id = c.id
        WHERE p.id = ?
    ''', (project_id,))
    project_info = cursor.fetchone()
    if not project_info:
        conn.close()
        return None

    name, description, deadline, github_url, manager_fio, customer_fio = project_info

    cursor.execute('''
        SELECT d.fio
        FROM developers d
        JOIN project_developers pd ON d.id = pd.developer_id
        WHERE pd.project_id = ?
        ORDER BY d.fio
    ''', (project_id,))
    developers = [row[0] for row in cursor.fetchall()]
    conn.close()

    return {
        'name': name,
        'description': description,
        'deadline': deadline,
        'github_url': github_url,
        'manager_fio': manager_fio,
        'customer_fio': customer_fio,
        'developers': developers
    }


def get_project_github_url(project_id: int):
    """
    Возвращает GitHub-ссылку проекта.

    :param project_id: id проекта.
    :return: строка со ссылкой или None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT github_url FROM projects WHERE id = ?',
        (project_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def update_project_github_url(project_id: int, github_url: str):
    """
    Обновляет GitHub-ссылку проекта.

    :param project_id: id проекта.
    :param github_url: новая ссылка.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE projects SET github_url = ? WHERE id = ?',
        (github_url, project_id)
    )
    conn.commit()
    conn.close()


def init_github_column():
    """
    Добавляет колонку github_url в таблицу projects, если её нет.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE projects ADD COLUMN github_url TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()


def create_project(name: str, description: str, deadline: str,
                   manager_id: int, customer_id: int):
    """
    Создаёт новый проект.

    :param name: название проекта.
    :param description: описание проекта.
    :param deadline: дедлайн (ГГГГ-ММ-ДД).
    :param manager_id: id руководителя.
    :param customer_id: id заказчика.
    :return: id созданного проекта.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO projects (name, description, deadline, manager_id, customer_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, description, deadline, manager_id, customer_id))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def init_archive_tables():
    """Создаёт таблицы для хранения бэкапов (архива) проектов."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archived_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_project_id INTEGER,
            name TEXT,
            description TEXT,
            deadline TEXT,
            github_url TEXT,
            manager_fio TEXT,
            customer_fio TEXT,
            archived_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archived_project_developers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archived_project_id INTEGER NOT NULL,
            developer_fio TEXT NOT NULL,
            FOREIGN KEY (archived_project_id)
                REFERENCES archived_projects(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()


def get_expired_projects():
    """
    Возвращает список проектов с истёкшим дедлайном.
    :return: список кортежей (id, name, deadline).
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.date.today().isoformat()  # '2026-10-24'
    cursor.execute('''
        SELECT id, name, deadline
        FROM projects
        WHERE deadline IS NOT NULL AND deadline != '' AND deadline < ?
        ORDER BY deadline ASC
    ''', (today,))
    result = cursor.fetchall()
    conn.close()
    return result


def archive_project(project_id: int):
    """
    Создаёт бэкап проекта: сохраняет название, описание, дедлайн,
    GitHub-ссылку, ФИО руководителя, заказчика и всех разработчиков.
    :param project_id: id архивируемого проекта.
    :return: True при успехе, False если проект не найден.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.id, p.name, p.description, p.deadline, p.github_url,
               m.fio, c.fio
        FROM projects p
        LEFT JOIN managers m ON p.manager_id = m.id
        LEFT JOIN customers c ON p.customer_id = c.id
        WHERE p.id = ?
    ''', (project_id,))
    project = cursor.fetchone()
    if not project:
        conn.close()
        return False

    orig_id, name, description, deadline, github_url, manager_fio, customer_fio = project

    cursor.execute('''
        INSERT INTO archived_projects
        (original_project_id, name, description, deadline,
         github_url, manager_fio, customer_fio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (orig_id, name, description, deadline,
          github_url, manager_fio, customer_fio))
    archived_id = cursor.lastrowid

    cursor.execute('''
        SELECT d.fio
        FROM developers d
        JOIN project_developers pd ON d.id = pd.developer_id
        WHERE pd.project_id = ?
    ''', (project_id,))
    developers = cursor.fetchall()

    for (dev_fio,) in developers:
        cursor.execute('''
            INSERT INTO archived_project_developers
            (archived_project_id, developer_fio)
            VALUES (?, ?)
        ''', (archived_id, dev_fio))

    conn.commit()
    conn.close()
    return True


def get_all_archived_projects():
    """
    Возвращает список всех архивных проектов (бэкапов).
    :return: список кортежей (id, original_project_id, name, description,
             deadline, github_url, manager_fio, customer_fio, archived_at).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, original_project_id, name, description, deadline,
               github_url, manager_fio, customer_fio, archived_at
        FROM archived_projects
        ORDER BY archived_at DESC
    ''')
    result = cursor.fetchall()
    conn.close()
    return result


def get_archived_project_info(archive_id: int):
    """
    Возвращает полную информацию об архивном проекте.
    :return: словарь или None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, description, deadline, github_url,
               manager_fio, customer_fio, archived_at
        FROM archived_projects WHERE id = ?
    ''', (archive_id,))
    info = cursor.fetchone()
    if not info:
        conn.close()
        return None

    cursor.execute('''
        SELECT developer_fio
        FROM archived_project_developers
        WHERE archived_project_id = ?
    ''', (archive_id,))
    developers = [row[0] for row in cursor.fetchall()]
    conn.close()

    return {
        'name': info[0],
        'description': info[1],
        'deadline': info[2],
        'github_url': info[3],
        'manager_fio': info[4],
        'customer_fio': info[5],
        'archived_at': info[6],
        'developers': developers
    }


def delete_archive(archive_id: int):
    """Удаляет бэкап проекта по его id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM archived_projects WHERE id = ?', (archive_id,))
    conn.commit()
    conn.close()