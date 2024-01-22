from pydantic import BaseModel
from typing import List

class _Source(BaseModel):
    url: str
    source: str
    tags: List[str]

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
    cvssMetricV2: List[_Score]

class CveExploit(BaseModel):
    id: str
    published: str
    vulnStatus: str
    descriptions: List[_Description]
    metrics: _Metrics
    references: List[_Source]