import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtCore import Qt
from login_window import LoginWindow
from developer_window import DeveloperWindow
from customer_window import CustomerWindow
from manager_window import ManagerWindow
import database

# Главный контроллер: управляет окнами и переключением между ролями
class AppController:
    def __init__(self):
        # Инициализируем таблицу чата при запуске
        database.init_chat_table()
        
        self.stack = QStackedWidget()
        self.stack.setWindowTitle("Софт контроль")
        self.stack.setMinimumSize(1200, 600)
        self.stack.setMaximumSize(1200, 600)
        
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.on_login_success)
        self.stack.addWidget(self.login_window)
        
        self.role_windows = {}
        self.stack.show()

    # Если пользователь успешно вошёл — открываем нужный кабинет
    def on_login_success(self, user_data: dict):
        role = user_data['role']
        if role in self.role_windows:
            self.stack.setCurrentWidget(self.role_windows[role])
            return

        if role == 'developer':
            window = DeveloperWindow(user_data)
        elif role == 'customer':
            window = CustomerWindow(user_data)
        elif role == 'manager':
            window = ManagerWindow(user_data)
        else:
            return

        window.logout_requested.connect(self.on_logout)
        self.role_windows[role] = window
        self.stack.addWidget(window)
        self.stack.setCurrentWidget(window)

    # При выходе чистим память и возвращаемся на экран логина
    def on_logout(self):
        for window in self.role_windows.values():
            self.stack.removeWidget(window)
            window.deleteLater()
        self.role_windows.clear()
        
        self.login_window.login_input.clear()
        self.login_window.password_input.clear()
        self.stack.setCurrentWidget(self.login_window)

# Точка входа
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    controller = AppController()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()