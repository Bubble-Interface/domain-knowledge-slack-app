from sqlalchemy import String, Integer
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column
)


class Base(DeclarativeBase):
    pass


class Knowledge(Base):
    __tablename__ = "knowledge"

    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: let the user know if the title value is not unique
    title: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[str] = mapped_column(String(512))
