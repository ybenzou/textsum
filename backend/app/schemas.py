from typing import List, Optional
from pydantic import BaseModel

class SummarizationRequest(BaseModel):
    text: str
    model_name: Optional[str] = None
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    do_sample: Optional[bool] = False


class SummarizationResponse(BaseModel):
    summary: str
    details: List[str]
    depth: int
    hierarchy: Optional[List[List[str]]] = None
