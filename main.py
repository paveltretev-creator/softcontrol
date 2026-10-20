import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtCore import Qt
from login_window import LoginWindow
from developer_window import DeveloperWindow
from customer_window import CustomerWindow
from manager_window import ManagerWindow
import database

class AppController:
    def __init__(self):
        database.init_chat_table()
        database.init_github_column()  # НОВОЕ: добавляем колонку GitHub
        
        self.stack = QStackedWidget()
        self.stack.setWindowTitle("Софт контроль")
        self.stack.setMinimumSize(1200, 600)
        self.stack.setMaximumSize(1200, 600)
        
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.on_login_success)
        self.stack.addWidget(self.login_window)
        
        self.role_windows = {}
        self.stack.show()

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

    def on_logout(self):
        for window in self.role_windows.values():
            self.stack.removeWidget(window)
            window.deleteLater()
        self.role_windows.clear()
        
        self.login_window.login_input.clear()
        self.login_window.password_input.clear()
        self.stack.setCurrentWidget(self.login_window)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    controller = AppController()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()