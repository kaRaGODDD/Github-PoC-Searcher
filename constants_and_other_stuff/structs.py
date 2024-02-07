from datetime import datetime
from typing import NamedTuple, List, Union
from constants_and_other_stuff.pydantic_models import GraphQLAnswerModel

class StringInterval(NamedTuple):
    first_interval: str 
    second_interval: str


class DatetimeInterval(NamedTuple):
    first_interval: datetime 
    second_interval: datetime


class CveIDComponents(NamedTuple):
    cve: str
    cve_year: int
    cve_id: int


class PoCModel(NamedTuple):
    description: str
    github_urls: [List[str]]


class CVEIDProcessing(NamedTuple):
    need: bool
    github_urls: List[str]


class POCData(NamedTuple):
    cve_id: str
    description: str
    formatted_references: str

class PocObject(NamedTuple):
    description: str
    github_url: str
