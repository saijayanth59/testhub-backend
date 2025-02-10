from fastapi import BaseModel, Field
from typing import Optional


class ImageModel(BaseModel):
    # Unique ID for the image
    id: Optional[str] = Field(alias="_id", default=None)
    pdf_id: str = Field(...)  # Link to the PDF
    page_number: int = Field(...)  # Page number
    image_data: str = Field(...)  # Base64-encoded compressed image
