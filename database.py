import sqlite3

DB_NAME = 'company_projects.db'

# Работаем с SQLite — тут вся логика общения с базой
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

# Ищем юзера сразу во всех трёх таблицах (разработчики, заказчики, руководители)
def authenticate_user(login: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    query = '''
        SELECT id, fio, 'developer' AS role FROM developers WHERE login = ? AND password = ?
        UNION ALL
        SELECT id, fio, 'customer'  AS role FROM customers  WHERE login = ? AND password = ?
        UNION ALL
        SELECT id, fio, 'manager'   AS role FROM managers   WHERE login = ? AND password = ?
    '''
    cursor.execute(query, (login, password, login, password, login, password))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'id': result[0],
            'fio': result[1],
            'role': result[2]
        }
    return None

def get_customer_projects(customer_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    # Projects с джойном менеджера — чтобы сразу тянуть его ФИО
    query = '''
        SELECT p.name, p.description, m.fio, p.deadline
        FROM projects p
        LEFT JOIN managers m ON p.manager_id = m.id
        WHERE p.customer_id = ?
    '''
    cursor.execute(query, (customer_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_manager_projects(manager_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    # Склеиваем разработчиков через GROUP_CONCAT, чтобы в таблице было красиво
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

def get_project_details(project_id: int):
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, fio FROM developers ORDER BY fio')
    result = cursor.fetchall()
    conn.close()
    return result

def get_project_developers(project_id: int):
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE projects SET name = ?, description = ? WHERE id = ?',
        (name, description, project_id)
    )
    conn.commit()
    conn.close()

# Тут хитро: удаляем старые связи и пишем новые, плюс обновляем current_project_id у самих разработчиков
def set_project_developers(project_id: int, new_developer_ids: list):
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