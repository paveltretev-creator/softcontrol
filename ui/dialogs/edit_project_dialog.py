from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
QTextEdit, QListWidget, QListWidgetItem,
QDialogButtonBox, QFormLayout)
from PyQt5.QtCore import Qt

# Диалог, где можно поменять название, описание и команду проекта
class EditProjectDialog(QDialog):
    def __init__(self, project_id: int, name: str, description: str,
                 all_developers: list, assigned_dev_ids: set, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.all_developers = all_developers
        self.setWindowTitle("Редактирование проекта")
        self.setMinimumWidth(500)
        self.init_ui(name, description, assigned_dev_ids)

    def init_ui(self, name, description, assigned_dev_ids):
        layout = QVBoxLayout()

        form = QFormLayout()

        self.name_input = QLineEdit(name or "")
        self.name_input.setPlaceholderText("Введите название проекта")
        form.addRow("Название проекта:", self.name_input)

        self.description_input = QTextEdit()
        self.description_input.setPlainText(description or "")
        self.description_input.setPlaceholderText("Введите описание проекта")
        self.description_input.setMaximumHeight(90)
        form.addRow("Описание:", self.description_input)

        layout.addLayout(form)

        layout.addWidget(QLabel("Состав разработчиков (отметьте галочками):"))
        self.developers_list = QListWidget()

        for dev_id, fio in self.all_developers:
            item = QListWidgetItem(fio)
            # id разработчика прячем внутри элемента — потом удобно собирать
            item.setData(Qt.UserRole, dev_id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if dev_id in assigned_dev_ids:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.developers_list.addItem(item)

        layout.addWidget(self.developers_list)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # Собираем обратно всё, что пользователь нагалочил
    def get_data(self):
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()

        dev_ids = []
        for i in range(self.developers_list.count()):
            item = self.developers_list.item(i)
            if item.checkState() == Qt.Checked:
                dev_ids.append(item.data(Qt.UserRole))

        return name, description, dev_ids