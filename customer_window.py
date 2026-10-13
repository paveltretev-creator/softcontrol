from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
QPushButton, QTableWidget, QTableWidgetItem,
QHeaderView, QMessageBox)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import pyqtSignal, Qt
import database

# Кабинет заказчика — показывает его проекты
class CustomerWindow(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, user_data: dict):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Софт контроль — Заказчик")
        self.setMinimumSize(800, 550)
        self.init_ui()
        self.load_projects()

    def init_ui(self):
        layout = QVBoxLayout()

        header = QLabel("Кабинет заказчика")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)

        user_info = QLabel(f"Пользователь: {self.user_data['fio']}")
        layout.addWidget(user_info)

        table_header_layout = QHBoxLayout()
        table_title = QLabel("Мои проекты:")
        table_title.setFont(QFont("Arial", 12, QFont.Bold))
        table_header_layout.addWidget(table_title)
        table_header_layout.addStretch()

        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.load_projects)
        table_header_layout.addWidget(refresh_btn)
        layout.addLayout(table_header_layout)

        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(4)
        self.projects_table.setHorizontalHeaderLabels([
            "Название проекта",
            "Краткое описание",
            "Руководитель проекта",
            "Дедлайн"
        ])

        self.projects_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.projects_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.projects_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.projects_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        layout.addWidget(self.projects_table)

        logout_btn = QPushButton("Выйти из системы")
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)
        self.setLayout(layout)

    # Достаём проекты из базы и пихаем в таблицу
    def load_projects(self):
        try:
            projects = database.get_customer_projects(self.user_data['id'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось загрузить проекты:\n{e}")
            return

        self.projects_table.setRowCount(0)

        # Если проектов нет — пишем об этом прямо в таблице
        if not projects:
            self.projects_table.setRowCount(1)
            empty_item = QTableWidgetItem("У вас пока нет назначенных проектов")
            empty_item.setForeground(QColor("gray"))
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.projects_table.setItem(0, 0, empty_item)
            self.projects_table.setSpan(0, 0, 1, 4)
            return

        self.projects_table.setRowCount(len(projects))
        for row, project in enumerate(projects):
            name, description, manager_fio, deadline = project

            name_item = QTableWidgetItem(name or "—")
            name_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.projects_table.setItem(row, 0, name_item)

            desc_item = QTableWidgetItem(description or "Описание отсутствует")
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.projects_table.setItem(row, 1, desc_item)

            manager_item = QTableWidgetItem(manager_fio or "Не назначен")
            manager_item.setTextAlignment(Qt.AlignCenter)
            self.projects_table.setItem(row, 2, manager_item)

            deadline_item = QTableWidgetItem(deadline or "—")
            deadline_item.setTextAlignment(Qt.AlignCenter)
            self.projects_table.setItem(row, 3, deadline_item)

        self.projects_table.resizeRowsToContents()

    # При каждом показе окна обновляем данные
    def showEvent(self, event):
        super().showEvent(event)
        self.load_projects()