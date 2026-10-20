import sqlite3

DB_NAME = 'company_projects.db'

def init_admins_table():
    """Создаёт таблицу администраторов и добавляет тестового админа"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Создаём таблицу администраторов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Проверяем, есть ли уже администраторы
    cursor.execute('SELECT COUNT(*) FROM admins')
    count = cursor.fetchone()[0]
    
    # Если таблица пустая — добавляем тестового администратора
    if count == 0:
        cursor.execute('''
            INSERT INTO admins (fio, login, password)
            VALUES (?, ?, ?)
        ''', ('Администров Админ Админович', 'admin', 'admin123'))
        print("✓ Добавлен тестовый администратор:")
        print("  Логин: admin")
        print("  Пароль: admin123")
    
    conn.commit()
    conn.close()
    print("✓ Таблица admins успешно создана/проверена")

if __name__ == '__main__':
    init_admins_table()