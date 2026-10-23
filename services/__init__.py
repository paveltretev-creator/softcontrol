# services/__init__.py
"""
Пакет сервисов. Содержит общую бизнес-логику и утилиты,
используемые в UI, чтобы не дублировать код в каждом окне.
"""

# Словарь маппинга ролей для чата (включая admin, которого не хватало в старых окнах)
ROLE_TEXT = {
    "developer": "Разработчик",
    "customer": "Заказчик",
    "manager": "Руководитель",
    "admin": "Администратор"
}

# Словарь месяцев для форматирования даты
MONTHS = {
    '01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля',
    '05': 'мая', '06': 'июня', '07': 'июля', '08': 'августа',
    '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'
}


def format_chat_messages(messages: list) -> str:
    """
    Форматирует список сырых сообщений из БД в HTML-строку для QTextEdit.
    :param messages: список кортежей (sender_fio, sender_role, message, timestamp).
    :return: готовая HTML-строка.
    """
    if not messages:
        return ""

    html_parts = []
    for sender_fio, sender_role, message, timestamp in messages:
        role = ROLE_TEXT.get(sender_role, "Пользователь")
        try:
            date_part = timestamp.split()[0]
            _, month, day = date_part.split('-')
            formatted_date = f"{int(day)} {MONTHS[month]}"
        except Exception:
            formatted_date = timestamp

        html_parts.append(
            f"<b>{sender_fio}</b> <i>({role}, {formatted_date})</i><br>{message}<br><br>"
        )
    return "".join(html_parts)