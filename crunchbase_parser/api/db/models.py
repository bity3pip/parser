from sqlalchemy.dialects.postgresql import UUID as PgUUID
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.db.config import Base

websiteinfo_industry = Table(
    'websiteinfo_industry',
    Base.metadata,
    Column('websiteinfo_id', ForeignKey('file_loader_websiteinfo.id'), primary_key=True),
    Column('companyindustry_id', ForeignKey('file_loader_companyindustry.id'), primary_key=True)
)

class WebsiteInfo(Base):
    __tablename__ = "file_loader_websiteinfo"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    uuid = Column(PgUUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)

    industry = relationship(
        'CompanyIndustry',
        secondary=websiteinfo_industry
    )

class CompanyIndustry(Base):
    __tablename__ = "file_loader_companyindustry"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(128), nullable=False, unique=True)

class FilePurpose(Base):
    __tablename__ = "file_loader_filepurpose"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    code = Column(String(4), unique=True, nullable=False)
    description = Column(String(128), nullable=False)

    fileuploads = relationship("FileUpload", back_populates="file_purpose", cascade="all, delete-orphan")

class FileUpload(Base):
    __tablename__ = "file_loader_fileupload"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    file = Column(String, nullable=False)
    file_purpose_id = Column(Integer, ForeignKey("file_loader_filepurpose.id", ondelete='PROTECT'), nullable=False, index=True)
    upload = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    additional_data = Column(JSON, nullable=True)
    file_purpose = relationship("FilePurpose", back_populates="fileuploads")
