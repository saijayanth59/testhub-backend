from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv
from bson import ObjectId
from utils import generation_config, prompt
from pdf2image import convert_from_bytes
import google.generativeai as genai
import json
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
image_collection = db["images"]


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash-8b", generation_config=generation_config)


@app.get("/")
def read_root():
    return {"message": "Welcome to the TestHub API!"}


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Uploads a PDF file, extracts images, processes questions using Gemini AI,
    and stores everything in MongoDB.
    """
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

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
        pdf_result = await pdf_collection.insert_one(pdf_document)
        pdf_id = str(pdf_result.inserted_id)

        background_tasks.add_task(extract_images_and_questions, file_bytes, pdf_id)

        return JSONResponse(
            status_code=201,
            content={"message": "PDF uploaded successfully.", "pdf_id": pdf_id, "status": "processing"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading PDF: {str(e)}")

async def extract_images_and_questions(pdf_bytes: bytes, pdf_id: str):
    """
    Extract images from a PDF file, save them to MongoDB, and process questions.
    """
    try:
        images = convert_from_bytes(pdf_bytes)

        for i, image in enumerate(images):
            image_bytes = image.tobytes()
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")

            image_doc = {"pdf_id": pdf_id, "image_data": encoded_image}
            image_result = await image_collection.insert_one(image_doc)
            image_id = str(image_result.inserted_id)

            res = model.generate_content([prompt, image])
            extracted_questions = json.loads(res.text)

            for question in extracted_questions:
                question_doc = {
                    "pdf_id": pdf_id,
                    "text": question["text"],
                    "options": question["options"],
                    "answer": question.get("answer"),
                    "image_id": image_id, 
                }
                await question_collection.insert_one(question_doc)

        # Mark PDF as processed
        await pdf_collection.update_one({"_id": ObjectId(pdf_id)}, {"$set": {"status": "processed", "processed_at": datetime.now(timezone.utc)}})

    except Exception as e:
        print(f"Error processing PDF {pdf_id}: {e}")


@app.get("/image/{image_id}")
async def get_image(image_id: str):
    """
    Retrieves a stored image from MongoDB, decodes it, and returns it.
    """
    image = await image_collection.find_one({"_id": ObjectId(image_id)})

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        image_data = base64.b64decode(image["image_data"])

        return Response(
            content=image_data,
            media_type="image/jpeg",
            headers={"Content-Disposition": f'attachment; filename="{image_id}.jpg"'},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving image: {str(e)}")

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


@app.get("/questions/{pdf_id}")
async def get_questions(pdf_id: str):
    """
    Retrieves all questions for a given PDF ID.
    """
    questions = await question_collection.find({"pdf_id": pdf_id}).to_list(length=None)

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found")

    return questions

