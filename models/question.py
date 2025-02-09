from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator

# MongoDB ObjectId support
PyObjectId = Annotated[str, BeforeValidator(str)]


class Question(BaseModel):
    """
    Represents a single extracted question from a PDF.

    Each question belongs to a specific PDF, identified by `pdf_id`. 
    It contains the question text, multiple options, and an optional correct answer.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None, description="Unique identifier for the question.")
    pdf_id: PyObjectId = Field(..., description="The ID of the uploaded PDF this question belongs to.")
    text: str = Field(..., description="The actual question text.")
    options: List[str] = Field(..., description="A list of possible answers (options) for the question.")
    answer: Optional[str] = Field(None, description="The correct answer for the question (if available).")
    image: Optional[str] = Field(None, description="URL or base64 string of an associated image (if applicable).")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "pdf_id": "60d5ec49f72e4e3fbd36f123",
                "text": "What is the capital of France?",
                "options": ["Berlin", "Paris", "Madrid", "Rome"],
                "answer": "Paris",
                "image": None,
            }
        },
    )