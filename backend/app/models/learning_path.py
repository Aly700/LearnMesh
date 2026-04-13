from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.content import TimestampMixin


class LearningPath(TimestampMixin, Base):
    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    items: Mapped[list["LearningPathItem"]] = relationship(
        back_populates="learning_path",
        cascade="all, delete-orphan",
        order_by="LearningPathItem.position",
    )

    @property
    def ordered_content(self) -> list["LearningPathItem"]:
        return self.items


class LearningPathItem(Base):
    __tablename__ = "learning_path_items"
    __table_args__ = (UniqueConstraint("learning_path_id", "position"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    learning_path_id: Mapped[int] = mapped_column(
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(40), nullable=False)
    content_id: Mapped[int] = mapped_column(Integer, nullable=False)
    content_slug: Mapped[str] = mapped_column(String(120), nullable=False)
    content_title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    learning_path: Mapped[LearningPath] = relationship(back_populates="items")
