from typing import Any, Dict

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.v1 import TYPE_CHECKING
from app.models.v1.base import BaseModel
from app.schemas import QuestionType, TestStatus

if TYPE_CHECKING:
    from app.models.v1.lectures import LectureModel
    from app.models.v1.themes import ThemeModel
    from app.models.v1.users import UserModel
    from app.models.v1.videos import VideoLectureModel


class TestModel(BaseModel):
    """
    Модель для представления тестов.

    Attributes:
        title (str): Название теста
        description (str): Описание теста
        status (TestStatus): Статус теста (draft, published, archived)
        duration (int): Длительность теста в минутах
        passing_score (int): Проходной балл
        max_attempts (int): Максимальное количество попыток
        popularity_count (int): Количество прохождения теста (популярность)
        theme_id (int): ID тематики
        author_id (int): ID автора теста
        video_lecture_id (int): ID связанной видео-лекции

    Relationships:
        questions (list[QuestionModel]): Список вопросов теста
        theme (ThemeModel): Связанная тематика
        author (UserModel): Автор теста
        video_lecture (VideoLectureModel): Связанная видео лекция
    """

    __tablename__ = "tests"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    # status: Mapped[TestStatus] = mapped_column(default=TestStatus.DRAFT)
    duration: Mapped[int] = mapped_column(nullable=False)  # в минутах
    passing_score: Mapped[int] = mapped_column(default=60, nullable=False)
    max_attempts: Mapped[int] = mapped_column(default=3, nullable=False)
    popularity_count: Mapped[int] = mapped_column(default=0, nullable=False)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    video_lecture_id: Mapped[int] = mapped_column(
        ForeignKey("video_lectures.id"), nullable=True
    )
    lecture_id: Mapped[int] = mapped_column(ForeignKey("lectures.id"), nullable=True)
    lecture: Mapped["LectureModel"] = relationship(
        "LectureModel", back_populates="tests", lazy="joined"
    )
    questions: Mapped[list["QuestionModel"]] = relationship(
        "QuestionModel",
        back_populates="test",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    theme: Mapped["ThemeModel"] = relationship(
        "ThemeModel", back_populates="tests", lazy="joined"
    )
    author: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="tests", lazy="joined"
    )
    video_lecture: Mapped["VideoLectureModel"] = relationship(
        "VideoLectureModel", back_populates="tests", lazy="joined"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "questions": [question.to_dict() for question in self.questions],
        }


class QuestionModel(BaseModel):
    """
    Модель вопроса в тесте

    Attributes:
        test_id (int): ID теста, к которому относится вопрос
        text (str): Текст вопроса
        type (QuestionType): Тип вопроса (single - один правильный ответ или multiple - несколько правильных ответов)
        points (int): Количество баллов за правильный ответ

    Relationships:
        test (TestModel): Связь с тестом, к которому относится вопрос
        answers (list[AnswerModel]): Связь с вариантами ответов на вопрос
    """

    __tablename__ = "questions"

    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[QuestionType] = mapped_column(nullable=False)
    points: Mapped[int] = mapped_column(default=1, nullable=False)

    test: Mapped["TestModel"] = relationship("TestModel", back_populates="questions")
    answers: Mapped[list["AnswerModel"]] = relationship(
        "AnswerModel",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "answers": [answer.to_dict() for answer in self.answers],
        }


class AnswerModel(BaseModel):
    """
    Модель варианта ответа на вопрос

    Attributes:
        question_id (int): ID вопроса, к которому относится ответ
        text (str): Текст ответа
        is_correct (bool): Флаг, указывающий, является ли ответ правильным

    Relationships:
        question (QuestionModel): Связь с вопросом, к которому относится ответ
    """

    __tablename__ = "answers"

    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False, nullable=False)

    question: Mapped["QuestionModel"] = relationship(
        "QuestionModel", back_populates="answers"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
        }
