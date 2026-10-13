from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal

# Пока это просто заглушка — функционал для разработчика ещё в работе
class DeveloperWindow(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, user_data: dict):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Софт контроль — Разработчик")
        self.setMinimumSize(700, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        header = QLabel(f"Кабинет разработчика")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)

        user_info = QLabel(f"Пользователь: {self.user_data['fio']}")
        layout.addWidget(user_info)

        placeholder = QLabel(
            "Здесь будет отображаться:\n"
            "• Список назначенных проектов\n"
            "• Задачи по каждому проекту\n"
            "• Статус выполнения задач\n"
            "• Отчёты о проделанной работе"
        )
        placeholder.setStyleSheet("background-color: #f0f0f0; padding: 20px;")
        layout.addWidget(placeholder)

        logout_btn = QPushButton("Выйти из системы")
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)
        self.setLayout(layout)