from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Preferences(Strict):
    max_price: float | None = Field(None, gt=0, le=1000000)
    min_price: float | None = Field(None, ge=0, le=1000000)
    currency: Literal['KES'] = 'KES'
    category: str | None = Field(None, max_length=100)
    brand: str | None = Field(None, max_length=80)
    required_labels: list[str] = Field(default_factory=list, max_length=8)
    excluded_ingredients: list[str] = Field(default_factory=list, max_length=8)
    in_stock: bool = False

    @model_validator(mode='after')
    def coherent(self):
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValueError('Minimum price cannot exceed maximum price.')
        if any(not x.strip() or len(x) > 60 for x in self.required_labels + self.excluded_ingredients):
            raise ValueError('Preference labels must contain 1–60 characters.')
        return self

class Turn(Strict):
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1, max_length=1200)

class ChatRequest(Strict):
    message: str = Field(min_length=2, max_length=1500)
    history: list[Turn] = Field(default_factory=list, max_length=8)
    preferences: Preferences = Field(default_factory=Preferences)
    k: int = Field(4, ge=1, le=5)

class Reference(Strict):
    id: str
    name: str
    description: str
    price: float | None
    currency: Literal['KES']
    url: str | None
    category: list[str]
    stock: Literal['unknown', 'in_stock', 'out_of_stock']
    source_record_id: str
    reason: str

class ChatResponse(Strict):
    answer: str
    references: list[Reference] = Field(default_factory=list)
    mode: str
    retrieval: str
    preferences: Preferences
    notices: list[str] = Field(default_factory=list)
    retry_after: int | None = None
    request_id: str
