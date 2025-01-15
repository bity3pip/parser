from fastapi import APIRouter, UploadFile, File, Form, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from api.db.models import FilePurpose, FileUpload, CompanyIndustry
from api.db.config import SessionLocal
from parser.selenium_parser import WebParserSelenium
from parser_helper.savers.industry_saver import IndustrySaver
from parser_helper.csv_reader.csv_reader import CSVMultiReader
from typing import List
import datetime
import os

router = APIRouter(tags=["Parser"])

MEDIA_ROOT = "/crunchbase_parser/shared_storage"
MEDIA_URL = "/media"

def get_codes_from_db():
    db = SessionLocal()
    codes = db.query(FilePurpose).all()
    db.close()
    return [code.code for code in codes]

def get_files_from_db():
    db = SessionLocal()
    files = db.query(FileUpload).all()
    db.close()
    return [file.file for file in files]

def get_industry_from_db():
    db = SessionLocal()
    industries = db.query(CompanyIndustry).all()
    db.close()
    return [industry.industry for industry in industries]


@router.post("/parse_industry/")
async def parse_urls(
        file: UploadFile = File(...),
        fields: List[str] = Form(...),
        output_file_name: str = Form(...),
        db: Session = Depends(get_industry_from_db),
        file_purpose_code: str = Query(..., enum=get_codes_from_db())
):
    try:
        file_record = db.query(FileUpload).filter(FileUpload.file == file).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found.")

        input_file_path = os.path.join(MEDIA_ROOT, file_record.file)

        fields = [field.split(",") for field in fields][0]

        parser = CSVMultiReader(fields, file_path=input_file_path)
        rows = parser.read_file()

        extractor = WebParserSelenium(data=rows)
        extractor.process_csv()
        industries = extractor.get_result()


        if not output_file_name.endswith(".csv"):
            output_file_name += ".csv"

        output_file_path = os.path.join(MEDIA_ROOT, output_file_name)
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        saver = IndustrySaver(output_file=output_file_path, data=industries)
        saver.save_result()

        file_url = os.path.join(MEDIA_URL, output_file_name)

        purpose = db.query(FilePurpose).filter(FilePurpose.code == file_purpose_code).first()
        if not purpose:
            raise HTTPException(status_code=400, detail=f"Invalid file purpose code: {file_purpose_code}")
        file_purpose_id = purpose.id

        try:
            db_file = FileUpload(
                file=output_file_name,
                file_purpose_id=file_purpose_id,
                upload=datetime.utcnow()
            )
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to add file to the database, {error}"
            )
        return {
            "status": "success",
            "message": "File successfully added to the database and accessible through media URL"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during email extraction: {str(e)}"
        )