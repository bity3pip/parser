from sqlalchemy.dialects.postgresql import UUID as PgUUID
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.db.config import Base



class FilePurpose(Base):
    __tablename__ = "file_loader_filepurpose"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    code = Column(String(4), unique=True, nullable=False)
    description = Column(String(128), nullable=False)

    fileuploads = relationship("FileUpload", back_populates="file_purpose")


class FileUpload(Base):
    __tablename__ = "file_loader_fileupload"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    file = Column(String, nullable=False)
    file_purpose_id = Column(Integer, ForeignKey("file_loader_filepurpose.id", ondelete='PROTECT'), nullable=False, index=True)
    upload = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    additional_data = Column(JSON, nullable=True)

    file_purpose = relationship("FilePurpose", back_populates="fileuploads")

class CompanyIndustry(Base):
    __tablename__ = "company_industries"
    id = Column(PgUUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False, unique=True)

