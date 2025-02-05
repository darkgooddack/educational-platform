from enum import Enum

class QuestionType(str, Enum):
    SINGLE = "single"  # один правильный ответ
    MULTIPLE = "multiple"  # несколько правильных ответов