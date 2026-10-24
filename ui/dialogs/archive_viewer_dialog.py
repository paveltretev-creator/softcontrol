"""
Диалог просмотра всех бэкапов (архива) проектов.
Позволяет посмотреть список сохранённых проектов с истёкшим дедлайном
и открыть подробную информацию о каждом из них.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from data import database
from ui.dialogs.project_info_dialog import ProjectInfoDialog


class ArchiveViewerDialog(QDialog):
    """Диалоговое окно со списком всех архивных проектов."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Архив проектов (бэкапы)")
        self.setMinimumSize(900, 500)
        self.init_ui()
        self.load_archives()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Архив проектов с истёкшим дедлайном")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_archives)
        btn_layout.addWidget(refresh_btn)

        self.info_btn = QPushButton("Информация")
        self.info_btn.clicked.connect(self.show_archive_info)
        btn_layout.addWidget(self.info_btn)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_archive)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        # Таблица архивов
        self.archive_table = QTableWidget()
        self.archive_table.setColumnCount(6)
        self.archive_table.setHorizontalHeaderLabels([
            "Название", "Дедлайн", "Руководитель",
            "Заказчик", "Дата архивации", "GitHub"
        ])
        header = self.archive_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.archive_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.archive_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.archive_table.setSelectionMode(QTableWidget.SingleSelection)
        self.archive_table.setAlternatingRowColors(True)
        self.archive_table.verticalHeader().setVisible(False)
        layout.addWidget(self.archive_table)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def load_archives(self):
        """Загружает список всех бэкапов из БД."""
        try:
            archives = database.get_all_archived_projects()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось загрузить архив:\n{e}")
            return

        self.archive_table.setRowCount(0)
        if not archives:
            self.archive_table.setRowCount(1)
            empty_item = QTableWidgetItem("Архив пуст")
            empty_item.setForeground(QColor("gray"))
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.archive_table.setItem(0, 0, empty_item)
            self.archive_table.setSpan(0, 0, 1, 6)
            return

        self.archive_table.setRowCount(len(archives))
        for row, arc in enumerate(archives):
            arc_id, orig_id, name, description, deadline, github_url, \
                manager_fio, customer_fio, archived_at = arc

            name_item = QTableWidgetItem(name or "—")
            name_item.setData(Qt.UserRole, arc_id)
            name_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.archive_table.setItem(row, 0, name_item)

            self.archive_table.setItem(
                row, 1, QTableWidgetItem(deadline or "—"))
            self.archive_table.setItem(
                row, 2, QTableWidgetItem(manager_fio or "Не назначен"))
            self.archive_table.setItem(
                row, 3, QTableWidgetItem(customer_fio or "Не указан"))
            self.archive_table.setItem(
                row, 4, QTableWidgetItem(archived_at or "—"))
            self.archive_table.setItem(
                row, 5, QTableWidgetItem(github_url or "—"))

        self.archive_table.resizeRowsToContents()

    def _get_selected_archive_id(self):
        selected = self.archive_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.information(
                self, "Внимание", "Сначала выберите запись в таблице")
            return None
        row = selected[0].row()
        item = self.archive_table.item(row, 0)
        if not item:
            return None
        return item.data(Qt.UserRole)

    def show_archive_info(self):
        """Открывает диалог с подробной информацией о выбранном бэкапе."""
        archive_id = self._get_selected_archive_id()
        if archive_id is None:
            return
        try:
            info = database.get_archived_project_info(archive_id)
            if not info:
                QMessageBox.warning(self, "Ошибка", "Бэкап не найден")
                return
            # ProjectInfoDialog принимает dict с ключами name, description,
            # deadline, github_url, manager_fio, customer_fio, developers
            dialog = ProjectInfoDialog(info, parent=self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось загрузить информацию:\n{e}")

    def delete_archive(self):
        """Удаляет выбранный бэкап после подтверждения."""
        archive_id = self._get_selected_archive_id()
        if archive_id is None:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Удалить выбранный бэкап из архива?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            database.delete_archive(archive_id)
            QMessageBox.information(self, "Успех", "Бэкап удалён")
            self.load_archives()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось удалить бэкап:\n{e}")