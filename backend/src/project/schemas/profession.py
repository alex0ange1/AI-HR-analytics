from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ProfessionCreateUpdateSchema(BaseModel):
    name: str
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


class ProfessionSchema(ProfessionCreateUpdateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
