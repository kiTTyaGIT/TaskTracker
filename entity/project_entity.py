from sqlalchemy import Column, Integer, Text, TIMESTAMP

from db import Base


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(Text)
    description = Column(Text)
    start_date = Column(TIMESTAMP(timezone=True))
    finish_date = Column(TIMESTAMP(timezone=True))

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"