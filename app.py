from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv
from bson import ObjectId
import motor.motor_asyncio
import os
import zlib
import base64

load_dotenv()

app = FastAPI(
    title="TestHub API",
)
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.hub
pdf_collection = db["pdfs"]
question_collection = db["questions"]


@app.get("/")
def read_root():
    return {"message": "Welcome to the TestHub API!"}


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Uploads a PDF file, compresses it, and stores it in MongoDB.

    - Converts file to Base64, compresses it, and saves in MongoDB.
    - Stores metadata (`name`, `status`, `timestamps`) in the database.
    - Returns the ID of the saved document.
    """
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400, detail="Only PDF files are allowed.")

        file_bytes = await file.read()
        compressed_data = zlib.compress(file_bytes)
        encoded_pdf = base64.b64encode(compressed_data).decode("utf-8")
        pdf_document = {
            "name": file.filename,
            "file": encoded_pdf,
            "status": "processing",
            "uploaded_at": datetime.now(timezone.utc),
            "processed_at": None,
        }

        result = await pdf_collection.insert_one(pdf_document)

        return JSONResponse(
            status_code=201,
            content={
                "message": "PDF uploaded successfully.",
                "pdf_id": str(result.inserted_id),
                "file_name": file.filename,
                "status": "processing",
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading PDF: {str(e)}")


@app.get("/pdf/{pdf_id}")
async def get_pdf(pdf_id: str):
    """
    Retrieves a stored PDF from MongoDB, decompresses it, and returns it.

    - Fetches the document by `_id`.
    - Decodes Base64 and decompresses the file.
    - Returns the PDF as a downloadable response.
    """
    document = await pdf_collection.find_one({"_id": ObjectId(pdf_id)})

    if not document:
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        compressed_data = base64.b64decode(document["file"])
        decompressed_pdf = zlib.decompress(compressed_data)

        return Response(
            content=decompressed_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{document["name"]}"'},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving PDF: {str(e)}")
