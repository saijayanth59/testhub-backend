from google import genai
from google.genai import types
import json
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def process_pdf(pdf_path):
    model = "gemini-2.5-flash-preview-04-17"
    config = types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema={
            "required": ["subject", "questions"],
            "type": "OBJECT",
            "properties": {
                "subject": {
                    "type": "STRING",
                    "description": "The subject of the PDF file."
                },
                "questions": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "required": ["question", "is_image_question", "answers"],
                        "properties": {
                            "question": {
                                "type": "STRING",
                                "description": "The question extracted from the PDF file."
                            },
                            "answers": {
                                "type": "ARRAY",
                                "items": {
                                    "type": "STRING",
                                    "description": "The answer to the question extracted from the PDF file."
                                },
                                "description": "The answers to the question extracted from the PDF file."
                            },
                            "options": {
                                "type": "ARRAY",
                                "items": {
                                    "type": "STRING",
                                    "description": "The options for the question extracted from the PDF file."
                                },
                                "description": "The options for the question extracted from the PDF file."
                            },
                            "is_image_question": {
                                "type": "BOOLEAN",
                                "description": "Does the question required image to answer"
                            },
                        }
                    },
                    "description": "The questions extracted from the PDF file."
                }
            },
        }
    )

    pdf = client.files.upload(file=pdf_path)

    response = client.models.generate_content(
        model=model,
        contents=["Extract questions, answers and options from the PDF file.", pdf],
        config=config
    ).text
    return json.loads(response)


if __name__ == "__main__":
    pdf_path = "test.pdf"
    result = process_pdf(pdf_path)
    print(result)
    with open("output.json", "w") as json_file:
        json.dump(result, json_file, indent=4)
