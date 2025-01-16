from fastapi import APIRouter, UploadFile, File, Form, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from api.db.models import FilePurpose, FileUpload, CompanyIndustry, WebsiteInfo
from api.db.config import SessionLocal
from api.db.getdbsession import get_db
from parser.selenium_parser import WebParserSelenium
from parser_helper.csv_reader.csv_reader import CSVMultiReader
from typing import List
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
        db: Session = Depends(get_db),
        file_purpose_code: str = Query(..., enum=get_codes_from_db())
):
    try:
        purpose = db.query(FilePurpose).filter(FilePurpose.code == file_purpose_code).first()
        if not purpose:
            raise HTTPException(status_code=400, detail=f"Invalid file purpose code: {file_purpose_code}")

        input_file_path = os.path.join(MEDIA_ROOT, file.filename)
        with open(input_file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        fields = fields[0].split(",") if isinstance(fields, list) else fields.split(",")
        parser = CSVMultiReader(fields, file_path=input_file_path)
        rows = parser.read_file()

        extractor = WebParserSelenium(data=rows)
        extractor.process_csv()
        industries = extractor.get_result()

        if not output_file_name.endswith(".csv"):
            output_file_name += ".csv"

        for item in industries:
            uuid = item["uuid"]
            industry_name = item["industry"].strip()[:128]
            if len(industry_name) > 128:
                industry_name = industry_name[:128]

            industry = db.query(CompanyIndustry).filter(CompanyIndustry.name == industry_name).first()
            if not industry:
                industry = CompanyIndustry(name=industry_name)
                db.add(industry)
                db.commit()
                db.refresh(industry)

            website_info = db.query(WebsiteInfo).filter(WebsiteInfo.uuid == uuid).first()
            if not website_info:
                raise HTTPException(status_code=400, detail=f"Invalid website info: {uuid}")

            if industry not in website_info.industry:
                website_info.industry.append(industry)

        db.commit()

        return {
            "status": "success",
            "message": "Industries processed and linked successfully."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error during industry processing: {str(e)}")
