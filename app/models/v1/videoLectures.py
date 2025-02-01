from app.models import BaseModel


class VideoLectureModel(BaseModel):
    __tablename__ = "videolectures"
    id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    theme: Mapped[str] = mapped_column(nullable=False)
    views: Mapped[str] = mapped_column(nullable=False)
    video_url: Mapped[str] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(nullable=False)

    # остальное потом создам
    