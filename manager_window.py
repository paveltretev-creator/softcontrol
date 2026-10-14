from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QTextEdit, QFrame, QLineEdit)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import pyqtSignal, Qt
import database
from edit_project_dialog import EditProjectDialog

# Кабинет руководителя — можно редактировать проекты и менять команду
class ManagerWindow(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, user_data: dict):
        super().__init__()
        self.user_data = user_data
        self.current_project_id = None
        self.setWindowTitle("Софт контроль — Руководитель")
        self.init_ui()
        self.load_projects()

    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("Кабинет руководителя")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)

        user_info = QLabel(f"Пользователь: {self.user_data['fio']}")
        layout.addWidget(user_info)

        content_layout = QHBoxLayout()

        # ЛЕВАЯ ЧАСТЬ: Таблица проектов
        left_layout = QVBoxLayout()
        
        table_header_layout = QHBoxLayout()
        table_title = QLabel("Мои проекты:")
        table_title.setFont(QFont("Arial", 12, QFont.Bold))
        table_header_layout.addWidget(table_title)
        table_header_layout.addStretch()

        self.edit_btn = QPushButton("✏️ Редактировать выбранный")
        self.edit_btn.clicked.connect(self.edit_selected_project)
        table_header_layout.addWidget(self.edit_btn)

        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.load_projects)
        table_header_layout.addWidget(refresh_btn)
        
        left_layout.addLayout(table_header_layout)

        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(4)
        self.projects_table.setHorizontalHeaderLabels([
            "Название проекта", "Описание", "Дедлайн", "Разработчики"
        ])
        header_view = self.projects_table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.projects_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.projects_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.projects_table.setSelectionMode(QTableWidget.SingleSelection)
        self.projects_table.setAlternatingRowColors(True)
        self.projects_table.verticalHeader().setVisible(False)
        self.projects_table.cellDoubleClicked.connect(self.edit_project_by_click)
        self.projects_table.currentCellChanged.connect(self.on_project_selected)
        
        left_layout.addWidget(self.projects_table)
        content_layout.addLayout(left_layout, 3)

        # ПРАВАЯ ЧАСТЬ: Окно чата
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
        try:
            projects = database.get_manager_projects(self.user_data['id'])
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
            project_id, name, description, deadline, developers = project
            name_item = QTableWidgetItem(name or "—")
            name_item.setData(Qt.UserRole, project_id)
            name_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.projects_table.setItem(row, 0, name_item)
            
            desc_item = QTableWidgetItem(description or "Описание отсутствует")
            self.projects_table.setItem(row, 1, desc_item)
            
            deadline_item = QTableWidgetItem(deadline or "—")
            deadline_item.setTextAlignment(Qt.AlignCenter)
            self.projects_table.setItem(row, 2, deadline_item)
            
            devs_item = QTableWidgetItem(developers or "Не назначены")
            self.projects_table.setItem(row, 3, devs_item)
            
        self.projects_table.resizeRowsToContents()

    def on_project_selected(self, row, col, prev_row, prev_col):
        if row < 0:
            return
        item = self.projects_table.item(row, 0)
        if not item:
            return
        self.current_project_id = item.data(Qt.UserRole)
        self.load_chat_messages()

    def load_chat_messages(self):
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

        # Словарь для преобразования ролей в текст
        role_text = {
            "developer": "Разработчик",
            "customer": "Заказчик",
            "manager": "Руководитель"
        }
        
        # Словарь месяцев на русском
        months = {
            '01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля',
            '05': 'мая', '06': 'июня', '07': 'июля', '08': 'августа',
            '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'
        }

        for sender_fio, sender_role, message, timestamp in messages:
            # Получаем текст роли
            role = role_text.get(sender_role, "Пользователь")
            
            # Парсим дату из timestamp (формат: "2026-10-14 15:30:45")
            try:
                date_part = timestamp.split()[0]  # "2026-10-14"
                year, month, day = date_part.split('-')
                formatted_date = f"{int(day)} {months[month]}"
            except:
                formatted_date = timestamp  # Если не удалось распарсить, показываем как есть
            
            # Форматируем сообщение
            formatted_msg = f"<b>{sender_fio}</b> <i>({role}, {formatted_date})</i><br>{message}<br><br>"
            self.chat_display.append(formatted_msg)
        
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
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

    def edit_project_by_click(self, row, col):
        self._open_edit_dialog(row)

    def edit_selected_project(self):
        selected = self.projects_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.information(self, "Внимание", "Сначала выберите проект в таблице")
            return
        row = selected[0].row()
        self._open_edit_dialog(row)

    def _open_edit_dialog(self, row: int):
        item = self.projects_table.item(row, 0)
        if not item:
            return
        project_id = item.data(Qt.UserRole)
        details = database.get_project_details(project_id)
        if not details:
            QMessageBox.warning(self, "Ошибка", "Проект не найден в БД")
            return

        name, description = details
        all_devs = database.get_all_developers()
        assigned_dev_ids = database.get_project_developers(project_id)

        dialog = EditProjectDialog(
            project_id=project_id, name=name, description=description,
            all_developers=all_devs, assigned_dev_ids=assigned_dev_ids, parent=self
        )

        if dialog.exec_() == EditProjectDialog.Accepted:
            new_name, new_description, new_dev_ids = dialog.get_data()
            if not new_name:
                QMessageBox.warning(self, "Ошибка", "Название проекта не может быть пустым")
                return
            try:
                database.update_project_info(project_id, new_name, new_description)
                database.set_project_developers(project_id, new_dev_ids)
                QMessageBox.information(self, "Успех", "Проект успешно обновлён")
                self.load_projects()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения:\n{e}")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_projects()