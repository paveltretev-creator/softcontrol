# ui/windows/customer_window.py
"""
Кабинет заказчика.
Отображает список проектов заказчика, позволяет просматривать
информацию о проекте и общаться в чате проекта.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QTextEdit, QFrame, QLineEdit)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import pyqtSignal, Qt

from data import database
from services import format_chat_messages
from ui.dialogs.project_info_dialog import ProjectInfoDialog


class CustomerWindow(QWidget):
    """Главное окно роли «Заказчик»."""
    logout_requested = pyqtSignal()

    def __init__(self, user_data: dict):
        """
        :param user_data: данные текущего пользователя (id, fio, role).
        """
        super().__init__()
        self.user_data = user_data
        self.current_project_id = None
        self.setWindowTitle("Софт контроль — Заказчик")
        self.init_ui()
        self.load_projects()

    def init_ui(self):
        """Создаёт интерфейс: заголовок, таблица проектов, чат, кнопка выхода."""
        layout = QVBoxLayout()
        header = QLabel("Кабинет заказчика")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        user_info = QLabel(f"Пользователь: {self.user_data['fio']}")
        layout.addWidget(user_info)
        content_layout = QHBoxLayout()
        # Левая часть — таблица проектов
        left_layout = QVBoxLayout()
        table_header_layout = QHBoxLayout()
        table_title = QLabel("Мои проекты:")
        table_title.setFont(QFont("Arial", 12, QFont.Bold))
        table_header_layout.addWidget(table_title)
        table_header_layout.addStretch()
        self.info_btn = QPushButton("Информация")
        self.info_btn.clicked.connect(self.show_project_info)
        table_header_layout.addWidget(self.info_btn)
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_projects)
        table_header_layout.addWidget(refresh_btn)
        left_layout.addLayout(table_header_layout)
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(4)
        self.projects_table.setHorizontalHeaderLabels([
            "Название проекта", "Краткое описание", "Руководитель проекта", "Дедлайн"
        ])
        self.projects_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.projects_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.projects_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.projects_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.projects_table.currentCellChanged.connect(self.on_project_selected)
        left_layout.addWidget(self.projects_table)
        content_layout.addLayout(left_layout, 3)
        # Правая часть — чат
        chat_frame = QFrame()
        chat_frame.setStyleSheet("QFrame { border: 1px solid #cccccc; border-radius: 5px; }")
        chat_layout = QVBoxLayout(chat_frame)
        chat_title = QLabel("Чат проекта")
        chat_title.setFont(QFont("Arial", 12, QFont.Bold))
        chat_layout.addWidget(chat_title)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Выберите проект для просмотра чата...")
        chat_layout.addWidget(self.chat_display)
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Введите сообщение...")
        self.chat_input.returnPressed.connect(self.send_message)
        chat_input_layout.addWidget(self.chat_input)
        send_btn = QPushButton("Отправить")
        send_btn.clicked.connect(self.send_message)
        chat_input_layout.addWidget(send_btn)
        chat_layout.addLayout(chat_input_layout)
        content_layout.addWidget(chat_frame, 1)
        layout.addLayout(content_layout)
        logout_btn = QPushButton("Выйти из системы")
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)
        self.setLayout(layout)

    def load_projects(self):
        """Загружает из БД и отображает проекты текущего заказчика."""
        try:
            projects = database.get_customer_projects(self.user_data['id'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить проекты:\n{e}")
            return
        self.projects_table.setRowCount(0)
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
            project_id, name, description, manager_fio, deadline = project
            name_item = QTableWidgetItem(name or "—")
            name_item.setData(Qt.UserRole, project_id)
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

    def on_project_selected(self, row, col, prev_row, prev_col):
        """
        Обработчик выбора строки в таблице.
        Сохраняет id выбранного проекта и загружает его чат.
        """
        if row < 0:
            return
        item = self.projects_table.item(row, 0)
        if not item:
            return
        self.current_project_id = item.data(Qt.UserRole)
        self.load_chat_messages()

    def show_project_info(self):
        """Открывает диалог с полной информацией о выбранном проекте."""
        selected = self.projects_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.information(self, "Внимание", "Сначала выберите проект в таблице")
            return
        row = selected[0].row()
        item = self.projects_table.item(row, 0)
        if not item:
            return
        project_id = item.data(Qt.UserRole)
        try:
            project_info = database.get_full_project_info(project_id)
            if not project_info:
                QMessageBox.warning(self, "Ошибка", "Проект не найден в БД")
                return
            dialog = ProjectInfoDialog(project_info, parent=self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить информацию:\n{e}")

    def load_chat_messages(self):
        """Загружает и отображает сообщения чата выбранного проекта."""
        if not self.current_project_id:
            self.chat_display.clear()
            self.chat_display.setPlaceholderText("Выберите проект для просмотра чата...")
            return
        try:
            messages = database.get_chat_messages(self.current_project_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить чат:\n{e}")
            return
        self.chat_display.clear()
        if not messages:
            self.chat_display.setPlaceholderText("Сообщений пока нет. Будьте первым!")
            return
        # Используем сервис вместо дублирующегося цикла
        html_content = format_chat_messages(messages)
        self.chat_display.setHtml(html_content)
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
        """Отправляет сообщение из поля ввода в чат выбранного проекта."""
        if not self.current_project_id:
            QMessageBox.warning(self, "Внимание", "Сначала выберите проект в таблице")
            return
        message = self.chat_input.text().strip()
        if not message:
            return
        try:
            database.save_chat_message(
                project_id=self.current_project_id,
                sender_id=self.user_data['id'],
                sender_role=self.user_data['role'],
                sender_fio=self.user_data['fio'],
                message=message
            )
            self.chat_input.clear()
            self.load_chat_messages()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отправить сообщение:\n{e}")

    def showEvent(self, event):
        """При каждом показе окна обновляет список проектов."""
        super().showEvent(event)
        self.load_projects()