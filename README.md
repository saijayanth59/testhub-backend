# TestHub API Documentation

## Overview

The **TestHub API** is designed to help students practice previous year exam papers in a realistic online exam environment. It allows users to upload PDFs, extract questions using AI, and retrieve them for exam preparation. The API uses **FastAPI**, **MongoDB**, and **Google Gemini AI** for question extraction.

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB database
- A valid **Google Gemini AI API key**

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/testhub-api.git
cd testhub-api

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file or set environment variables in your system:

```
MONGODB_URL=your_mongoDB_url
GEMINI_API_KEY=your_gemini_api_key
```

### Running the API

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## API Endpoints

### **1. Upload PDF**

**Endpoint:** `POST /upload-pdf/`

**Description:** Uploads a PDF file, extracts images, processes questions using AI, and stores everything in MongoDB.

**Request:**

- `file`: PDF file (multipart/form-data)

**Response:**

```json
{
  "message": "PDF uploaded successfully.",
  "pdf_id": "60e7f9d4f12c4b001c5b8e7a",
  "status": "processing"
}
```

### **2. Retrieve a PDF**

**Endpoint:** `GET /pdf/{pdf_id}`

**Description:** Retrieves a stored PDF from MongoDB, decompresses it, and returns it along with its status.

**Response:**

- Returns the PDF file with a custom header `X-PDF-Status`.

### **3. Get Questions for a PDF**

**Endpoint:** `GET /questions/{pdf_id}`

**Description:** Retrieves all extracted questions for a given PDF.

**Response:**

```json
[
  {
    "_id": "60e7f9d4f12c4b001c5b8e7b",
    "pdf_id": "60e7f9d4f12c4b001c5b8e7a",
    "question_text": "What is AI?",
    "options": ["A", "B", "C", "D"],
    "answer": "A",
    "page_number": 1,
    "contains_figure_or_diagram": false
  }
]
```

### **4. Get All Questions**

**Endpoint:** `GET /questions`

**Description:** Retrieves all extracted questions from the database.

**Response:**
Returns a list of all questions.

### **5. Get All PDFs**

**Endpoint:** `GET /pdfs`

**Description:** Retrieves all PDFs stored in the database.

**Response:**
Returns a list of PDFs.

---

## Wanna Contribute?

Read [CONTRIBUTE.md](./CONTRIBUTE.md) for guidelines on how to contribute.