from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QDialogButtonBox, QMessageBox)
from PyQt5.QtCore import Qt
import re

class GitHubDialog(QDialog):
    def __init__(self, current_url: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ссылка на GitHub")
        self.setMinimumWidth(400)
        self.current_url = current_url
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        label = QLabel("Введите ссылку на репозиторий GitHub:")
        layout.addWidget(label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://github.com/username/repository")
        self.url_input.setText(self.current_url or "")
        layout.addWidget(self.url_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def validate_and_accept(self):
        url = self.url_input.text().strip()
        
        if not url:
            # Пустая ссылка — разрешаем (можно удалить ссылку)
            self.accept()
            return
        
        url_pattern = re.compile(
            r'^https?://'  # http:// или https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # домен
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...или ip
            r'(?::\d+)?'  # опциональный порт
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            QMessageBox.warning(self, "Ошибка", "Некорректный формат URL")
            return
        
        if 'github.com' not in url.lower():
            reply = QMessageBox.question(
                self, "Предупреждение",
                "Ссылка не содержит 'github.com'. Сохранить всё равно?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        self.accept()

    def get_url(self):
        return self.url_input.text().strip()