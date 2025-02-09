from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]


class UploadedPDFModel(BaseModel):
    """
    Represents an uploaded PDF file that contains a set of questions.

    This model tracks the PDF file, its processing status, and timestamps 
    for when it was uploaded and processed.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None, description="Unique identifier for the uploaded PDF.")
    name: str = Field(..., description="Original name of the uploaded PDF file.")
    file: str = Field(..., description="Storage path or URL of the uploaded PDF file.")
    status: Optional[str] = Field(default="processing", description="Processing status of the PDF (e.g., 'processing', 'completed').")
    uploaded_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of when the PDF was uploaded.")
    processed_at: Optional[datetime] = Field(None, description="Timestamp of when the PDF processing was completed.")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Sample Exam Paper",
                "file": "https://example.com/sample.pdf",
                "status": "processing",
                "uploaded_at": "2025-02-09T12:00:00Z",
                "processed_at": None,
            }
        },
    )
