"""
Диалог создания нового проекта.

Позволяет ввести название, описание, дедлайн, а также выбрать
руководителя и заказчика из списков.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QTextEdit, QComboBox, QDialogButtonBox, QFormLayout)
from PyQt5.QtCore import Qt


class CreateProjectDialog(QDialog):
    """Диалоговое окно для создания нового проекта."""

    def __init__(self, managers: list, customers: list, parent=None):
        """
        :param managers: список кортежей (id, fio) руководителей.
        :param customers: список кортежей (id, fio) заказчиков.
        :param parent: родительский виджет.
        """
        super().__init__(parent)
        self.managers = managers
        self.customers = customers
        self.setWindowTitle("Создание нового проекта")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        """Формирует интерфейс диалога: поля ввода и комбобоксы."""
        layout = QVBoxLayout()
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название проекта")
        form.addRow("Название проекта:", self.name_input)

        self.description_input = QTextEdit()
        self.description_input.setPlainText("")
        self.description_input.setPlaceholderText("Введите описание проекта")
        self.description_input.setMaximumHeight(90)
        form.addRow("Описание:", self.description_input)

        self.deadline_input = QLineEdit()
        self.deadline_input.setPlaceholderText("ГГГГ-ММ-ДД")
        form.addRow("Дедлайн:", self.deadline_input)

        self.manager_combo = QComboBox()
        for manager_id, fio in self.managers:
            self.manager_combo.addItem(fio, manager_id)
        form.addRow("Руководитель проекта:", self.manager_combo)

        self.customer_combo = QComboBox()
        for customer_id, fio in self.customers:
            self.customer_combo.addItem(fio, customer_id)
        form.addRow("Заказчик:", self.customer_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        """
        Возвращает введённые пользователем данные.

        :return: кортеж (name, description, deadline, manager_id, customer_id).
        """
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        deadline = self.deadline_input.text().strip()
        manager_id = self.manager_combo.currentData()
        customer_id = self.customer_combo.currentData()
        return name, description, deadline, manager_id, customer_id