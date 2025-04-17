from typing import Dict, Any, Optional, List
from datetime import date
from pydantic import BaseModel, Field, ConfigDict

from project.schemas.profession import ProfessionSchema, ProfessionCreateUpdateSchema


class ResumeCreateUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    city: Optional[str] = None
    phone: str
    email: Optional[str] = None
    competencies: Dict[str, Any] = Field(
        default_factory=dict,
        examples=[{
            "competencies": [
                {
                    "name": "Языки программирования и библиотеки (Python, C++)",
                    "level": 2
                },
                {
                    "name": "Методы оптимизации",
                    "level": 2
                }
            ]
        }]
    )


class ResumeSchema(ResumeCreateUpdateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ResumeListResponse(BaseModel):
    resumes: List[ResumeSchema]


class FileUploadSchema(BaseModel):
    filename: str
    content: str


class MultiFileUploadSchema(BaseModel):
    files: List[FileUploadSchema]
    profession: ProfessionSchema


class ProcessedResumeResponse(BaseModel):
    resume_ids: List[int]
    status: str
