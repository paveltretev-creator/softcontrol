from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel,
QLineEdit, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
import database

# Окно входа в систему
class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Софт контроль — Вход")
        self.setFixedSize(280, 180)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)

        title = QLabel("Софт контроль")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(6)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        self.login_input.setFixedHeight(25)
        self.login_input.setStyleSheet("padding: 2px 5px;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(25)
        self.password_input.setStyleSheet("padding: 2px 5px;")

        form.addRow("Логин:", self.login_input)
        form.addRow("Пароль:", self.password_input)
        layout.addLayout(form)

        self.login_button = QPushButton("Войти")
        self.login_button.setFixedHeight(28)
        self.login_button.clicked.connect(self.try_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        # Enter в поле пароля тоже пытается войти
        self.password_input.returnPressed.connect(self.try_login)

    # Пытаемся войти: проверяем логин и пароль через базу
    def try_login(self):
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