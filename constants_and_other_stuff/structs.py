from datetime import datetime
from typing import NamedTuple, List

class StringInterval(NamedTuple):
    first_interval: str 
    second_interval: str


class DatetimeInterval(NamedTuple):
    first_interval: datetime 
    second_interval: datetime


class CvePattern(NamedTuple):
    cve_id: str
    published_date: str
    description: str
    url: str
    access_vector: str
    access_complexity: str
    base_severity: str
    vulnerability_status: str
    exploitability_score: int
    impact_score: int
    base_score: int
    references: List[str]