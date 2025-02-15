from flake8.formatting import base

class BriefFormatter(base.BaseFormatter):
    def format(self, error):
        # Группируем ошибки по коду
        code = error.code
        if code == 'E501':
            return f"Длинная строка > 88 символов: {error.filename}"
        elif code == 'F821':
            return f"Неопределенная переменная: {error.filename} -> {error.text}"
        elif code == 'F841':
            return f"Неиспользуемая переменная: {error.filename} -> {error.text}"
        elif code == 'W605':
            return f"Некорректный escape в regex: {error.filename}"
        elif code == 'E262':
            return f"Неправильный комментарий: {error.filename}"
        return f"{error.code}: {error.filename} -> {error.text}"