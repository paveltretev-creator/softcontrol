"""
Диалог ввода/редактирования GitHub-ссылки проекта.

Проверяет корректность URL и предупреждает, если ссылка
не ведёт на github.com.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QDialogButtonBox, QMessageBox)
from PyQt5.QtCore import Qt
import re


class GitHubDialog(QDialog):
    """Диалоговое окно для ввода ссылки на GitHub-репозиторий."""

    def __init__(self, current_url: str = "", parent=None):
        """
        :param current_url: текущая сохранённая ссылка (может быть пустой).
        :param parent: родительский виджет.
        """
        super().__init__(parent)
        self.setWindowTitle("Ссылка на GitHub")
        self.setMinimumWidth(400)
        self.current_url = current_url
        self.init_ui()

    def init_ui(self):
        """Формирует интерфейс: подсказка, поле ввода URL и кнопки."""
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
        """
        Проверяет введённый URL и закрывает диалог при успехе.

        Пустая ссылка разрешена (используется для очистки).
        Некорректный URL блокирует закрытие.
        Ссылка без 'github.com' вызывает предупреждение.
        """
        url = self.url_input.text().strip()
        if not url:
            self.accept()
            return

        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
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
        """
        Возвращает введённый URL.

        :return: строка с URL (без пробелов по краям).
        """
        return self.url_input.text().strip()