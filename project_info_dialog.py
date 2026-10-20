from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit,
                             QDialogButtonBox, QFormLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ProjectInfoDialog(QDialog):
    def __init__(self, project_info: dict, parent=None):
        super().__init__(parent)
        self.project_info = project_info
        self.setWindowTitle("Информация о проекте")
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel(self.project_info['name'] or "Без названия")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        form = QFormLayout()
        
        desc_label = QLabel("Описание:")
        desc_label.setFont(QFont("Arial", 10, QFont.Bold))
        form.addRow(desc_label)
        
        desc_text = QTextEdit()
        desc_text.setPlainText(self.project_info['description'] or "Описание отсутствует")
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(100)
        form.addRow(desc_text)
        
        deadline_label = QLabel("Дедлайн:")
        deadline_label.setFont(QFont("Arial", 10, QFont.Bold))
        form.addRow(deadline_label)
        form.addRow(QLabel(self.project_info['deadline'] or "Не установлен"))
        
        manager_label = QLabel("Руководитель проекта:")
        manager_label.setFont(QFont("Arial", 10, QFont.Bold))
        form.addRow(manager_label)
        form.addRow(QLabel(self.project_info['manager_fio'] or "Не назначен"))
        
        customer_label = QLabel("Заказчик:")
        customer_label.setFont(QFont("Arial", 10, QFont.Bold))
        form.addRow(customer_label)
        form.addRow(QLabel(self.project_info['customer_fio'] or "Не указан"))
        
        github_label = QLabel("GitHub:")
        github_label.setFont(QFont("Arial", 10, QFont.Bold))
        form.addRow(github_label)
        
        github_url = self.project_info.get('github_url')
        if github_url:
            github_link = QLabel(f'<a href="{github_url}">{github_url}</a>')
            github_link.setOpenExternalLinks(True)
            github_link.setStyleSheet("color: blue; text-decoration: underline;")
        else:
            github_link = QLabel("Ссылка не указана")
            github_link.setStyleSheet("color: gray;")
        form.addRow(github_link)
        
        devs_label = QLabel("Команда разработчиков:")
        devs_label.setFont(QFont("Arial", 10, QFont.Bold))
        form.addRow(devs_label)
        
        if self.project_info['developers']:
            devs_text = "\n".join(f"• {dev}" for dev in self.project_info['developers'])
        else:
            devs_text = "Разработчики не назначены"
        
        devs_display = QTextEdit()
        devs_display.setPlainText(devs_text)
        devs_display.setReadOnly(True)
        devs_display.setMaximumHeight(120)
        form.addRow(devs_display)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)