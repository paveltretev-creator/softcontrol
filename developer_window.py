from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import pyqtSignal, Qt
import database

# Кабинет разработчика — только просмотр, редактировать нельзя
class DeveloperWindow(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, user_data: dict):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Софт контроль — Разработчик")
        self.init_ui()
        self.load_projects()

    def init_ui(self):
        layout = QVBoxLayout()

        header = QLabel("Кабинет разработчика")
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

        # Таблица на 5 колонок: название, описание, дедлайн, руководитель, статус
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(5)
        self.projects_table.setHorizontalHeaderLabels([
            "Название проекта",
            "Описание",
            "Дедлайн",
            "Руководитель",
            "Статус"
        ])

        header_view = self.projects_table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # Блокируем редактирование — разработчик только смотрит
        self.projects_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.projects_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.projects_table.setSelectionMode(QTableWidget.SingleSelection)
        self.projects_table.setAlternatingRowColors(True)
        self.projects_table.verticalHeader().setVisible(False)

        layout.addWidget(self.projects_table)

        logout_btn = QPushButton("Выйти из системы")
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

        self.setLayout(layout)

    # Пихаем проекты из базы в таблицу
    def load_projects(self):
        try:
            projects = database.get_developer_projects(self.user_data['id'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось загрузить проекты:\n{e}")
            return

        self.projects_table.setRowCount(0)

        # Если проектов нет — пишем об этом прямо в таблице
        if not projects:
            self.projects_table.setRowCount(1)
            empty_item = QTableWidgetItem("Вы пока не назначены ни на один проект")
            empty_item.setForeground(QColor("gray"))
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.projects_table.setItem(0, 0, empty_item)
            self.projects_table.setSpan(0, 0, 1, 5)
            return

        self.projects_table.setRowCount(len(projects))

        for row, project in enumerate(projects):
            project_id, name, description, deadline, manager_fio = project

            name_item = QTableWidgetItem(name or "—")
            name_item.setData(Qt.UserRole, project_id)
            name_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.projects_table.setItem(row, 0, name_item)

            desc_item = QTableWidgetItem(description or "Описание отсутствует")
            self.projects_table.setItem(row, 1, desc_item)

            deadline_item = QTableWidgetItem(deadline or "—")
            deadline_item.setTextAlignment(Qt.AlignCenter)
            self.projects_table.setItem(row, 2, deadline_item)

            manager_item = QTableWidgetItem(manager_fio or "Не назначен")
            manager_item.setTextAlignment(Qt.AlignCenter)
            self.projects_table.setItem(row, 3, manager_item)

            # Пока статус заглушка — потом можно подтянуть из таблицы задач
            status_item = QTableWidgetItem("В работе")
            status_item.setTextAlignment(Qt.AlignCenter)
            self.projects_table.setItem(row, 4, status_item)

        self.projects_table.resizeRowsToContents()

    # При каждом показе окна обновляем данные
    def showEvent(self, event):
        super().showEvent(event)
        self.load_projects()