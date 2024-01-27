from pydantic import BaseModel, Field
from typing import List, Optional
import json


class Item(BaseModel):
    html_url: str

class HtmlUrlFromResponse(BaseModel):
    total_count: int
    items: Optional[List[Item]] = Field(None,alias='items')

class _Source(BaseModel):
    url: str
    source: str
    tags: Optional[List[str]] = Field(None, alias='tags')

class _CvssData(BaseModel):
    accessVector: str
    baseScore: float

class _Score(BaseModel):
    exploitabilityScore: float
    impactScore: float
    baseSeverity: str
    source: str
    cvssData: _CvssData

class _Description(BaseModel):
    lang: str
    value: str

class _Metrics(BaseModel):
    cvssMetricV2: Optional[List[_Score]] = []

class CveExploit(BaseModel):
    id: str
    published: str
    vulnStatus: str
    descriptions: List[_Description]
    metrics: _Metrics
    references: List[_Source]
    