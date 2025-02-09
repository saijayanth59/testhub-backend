import os
import google.generativeai as genai
from dotenv import load_dotenv
from constants import generation_config, prompt
from pdf2image import convert_from_path
import json


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)


def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    return file


model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-8b",
    generation_config=generation_config,
)


def extract_images_from_pdf(pdf_path, output_dir="output_images"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    images = convert_from_path(pdf_path)
    questions = []
    for i, image in enumerate(images):
        res = model.generate_content([prompt, image])
        questions.extend(json.loads(res.text))
        print(f"Extracted question {i+1} from the input image.")

    with open("result.json", "w", encoding="utf-8") as json_file:
        json.dump(questions, json_file, ensure_ascii=False, indent=4)

    return questions


if __name__ == "__main__":
    pdf_path = "GATE2007-3-5.pdf"
    print(extract_images_from_pdf(pdf_path))
