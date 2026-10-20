"""
Главный модуль приложения «Софт контроль».

Запускает PyQt5-приложение, управляет стеком окон (QStackedWidget)
и переключением между окнами в зависимости от роли авторизованного
пользователя (разработчик, заказчик, руководитель, администратор).
"""
import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtCore import Qt
from login_window import LoginWindow
from developer_window import DeveloperWindow
from customer_window import CustomerWindow
from manager_window import ManagerWindow
from admin_window import AdminWindow
import database


class AppController:
    """
    Контроллер приложения.

    Создаёт главное окно-стек, окно входа и окна для каждой роли.
    Обрабатывает события успешного входа и выхода из системы.
    """

    def __init__(self):
        """Инициализация контроллера: создание стека окон и окна входа."""
        database.init_chat_table()
        database.init_github_column()

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
        """
        Обработчик успешной авторизации.

        :param user_data: словарь с данными пользователя
                          (id, fio, role).
        Создаёт окно нужной роли (если его ещё нет) и показывает его.
        """
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
        elif role == 'admin':
            window = AdminWindow(user_data)
        else:
            return

        window.logout_requested.connect(self.on_logout)
        self.role_windows[role] = window
        self.stack.addWidget(window)
        self.stack.setCurrentWidget(window)

    def on_logout(self):
        """
        Обработчик выхода из системы.

        Удаляет все окна ролей, очищает поля ввода логина/пароля
        и возвращает пользователя на окно входа.
        """
        for window in self.role_windows.values():
            self.stack.removeWidget(window)
            window.deleteLater()
        self.role_windows.clear()

        self.login_window.login_input.clear()
        self.login_window.password_input.clear()
        self.stack.setCurrentWidget(self.login_window)


def main():
    """Точка входа: запуск QApplication и главного контроллера."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    controller = AppController()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()