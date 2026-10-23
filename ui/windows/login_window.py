# ui/windows/login_window.py
"""
Окно авторизации пользователя.
Содержит поля ввода логина и пароля, кнопку «Войти»
и отправляет сигнал login_success при успешной проверке.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from data import database


class LoginWindow(QWidget):
    """Виджет окна входа в систему «Софт контроль»."""
    login_success = pyqtSignal(dict)

    def __init__(self):
        """Создаёт окно и инициализирует интерфейс."""
        super().__init__()
        self.setWindowTitle("Софт контроль — Вход")
        self.init_ui()

    def init_ui(self):
        """Формирует визуальную часть окна: заголовок, поля, кнопку."""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)
        title = QLabel("Софт контроль")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addStretch()
        login_row = QHBoxLayout()
        login_row.addStretch()
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        self.login_input.setFixedWidth(180)
        self.login_input.setFixedHeight(25)
        self.login_input.setStyleSheet("padding: 2px 5px;")
        login_row.addWidget(self.login_input)
        login_row.addStretch()
        layout.addLayout(login_row)
        password_row = QHBoxLayout()
        password_row.addStretch()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(180)
        self.password_input.setFixedHeight(25)
        self.password_input.setStyleSheet("padding: 2px 5px;")
        password_row.addWidget(self.password_input)
        password_row.addStretch()
        layout.addLayout(password_row)
        button_row = QHBoxLayout()
        button_row.addStretch()
        self.login_button = QPushButton("Войти")
        self.login_button.setFixedWidth(120)
        self.login_button.setFixedHeight(28)
        self.login_button.clicked.connect(self.try_login)
        button_row.addWidget(self.login_button)
        button_row.addStretch()
        layout.addLayout(button_row)
        layout.addStretch()
        self.setLayout(layout)
        self.password_input.returnPressed.connect(self.try_login)

    def try_login(self):
        """
        Пытается авторизовать пользователя по введённым данным.
        При успехе испускает сигнал login_success с данными пользователя,
        при неудаче показывает сообщение об ошибке.
        """
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        user = database.authenticate_user(login, password)
        if user:
            self.login_success.emit(user)
        else:
            QMessageBox.critical(self, "Ошибка входа",
                                 "Неверный логин или пароль!")
            self.password_input.clear()
            self.password_input.setFocus()