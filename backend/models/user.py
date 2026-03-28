from sqlalchemy import JSON, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    embeddings: Mapped[list["UserEmbedding"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attendances: Mapped[list["Attendance"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class UserEmbedding(Base):
    __tablename__ = "user_embeddings"
    __table_args__ = (UniqueConstraint("user_id", "source_label", name="uq_user_embedding_source"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source_label: Mapped[str] = mapped_column(String(255))
    embedding: Mapped[list[float]] = mapped_column(JSON)

    user: Mapped["User"] = relationship(back_populates="embeddings")


from backend.models.attendance import Attendance  # noqa: E402
