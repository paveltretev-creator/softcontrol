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

# Достаём проекты, в которых участвует разработчик, сразу с руководителем
def get_developer_projects(developer_id: int):
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

# ============ НОВЫЕ ФУНКЦИИ ДЛЯ ЧАТА ============

def init_chat_table():
    """Создаёт таблицу для сообщений чата, если её ещё нет"""
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
    """Сохраняет сообщение в базу данных"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_messages (project_id, sender_id, sender_role, sender_fio, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (project_id, sender_id, sender_role, sender_fio, message))
    conn.commit()
    conn.close()

def get_chat_messages(project_id: int):
    """Получает все сообщения для указанного проекта, отсортированные по времени"""
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