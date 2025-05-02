from typing import List, Optional, Union
from pydantic import BaseModel

class SummarizationRequest(BaseModel):
    text: str
    model_name: Optional[str] = None
    do_sample: Optional[bool] = False

class SummaryBlock(BaseModel):
    text: str
    sources: Optional[List[int]] = None  # 引用上层 index 列表

class SummarizationResponse(BaseModel):
    summary: str
    details: List[str]
    depth: int
    hierarchy: List[List[Union[str, SummaryBlock]]]
