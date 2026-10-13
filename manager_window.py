from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
QPushButton, QTableWidget, QTableWidgetItem,
QHeaderView, QMessageBox)
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
        self.setWindowTitle("Софт контроль — Руководитель")
        self.setMinimumSize(900, 600)
        self.init_ui()
        self.load_projects()

    def init_ui(self):
        layout = QVBoxLayout()

        header = QLabel("Кабинет руководителя")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)

        user_info = QLabel(f"Пользователь: {self.user_data['fio']}")
        layout.addWidget(user_info)

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
        layout.addLayout(table_header_layout)

        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(4)
        self.projects_table.setHorizontalHeaderLabels([
            "Название проекта",
            "Описание",
            "Дедлайн",
            "Разработчики"
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

        # Двойной клик по строке открывает окно редактирования
        self.projects_table.cellDoubleClicked.connect(self.edit_project_by_click)

        layout.addWidget(self.projects_table)

        logout_btn = QPushButton("Выйти из системы")
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)
        self.setLayout(layout)

    def load_projects(self):
        try:
            projects = database.get_manager_projects(self.user_data['id'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось загрузить проекты:\n{e}")
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

    def edit_project_by_click(self, row, col):
        self._open_edit_dialog(row)

    def edit_selected_project(self):
        selected = self.projects_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.information(self, "Внимание",
                                    "Сначала выберите проект в таблице")
            return
        row = selected[0].row()
        self._open_edit_dialog(row)

    # Открываем диалог: подтягиваем детали проекта и всех разработчиков
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
            project_id=project_id,
            name=name,
            description=description,
            all_developers=all_devs,
            assigned_dev_ids=assigned_dev_ids,
            parent=self
        )

        if dialog.exec_() == EditProjectDialog.Accepted:
            new_name, new_description, new_dev_ids = dialog.get_data()

            if not new_name:
                QMessageBox.warning(self, "Ошибка",
                                    "Название проекта не может быть пустым")
                return

            # Сохраняем изменения и обновляем таблицу
            try:
                database.update_project_info(project_id, new_name, new_description)
                database.set_project_developers(project_id, new_dev_ids)
                QMessageBox.information(self, "Успех",
                                        "Проект успешно обновлён")
                self.load_projects()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось сохранить изменения:\n{e}")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_projects()