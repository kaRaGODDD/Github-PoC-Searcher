from datetime import datetime
from typing import List, NamedTuple, Union

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


class POCModel(NamedTuple):
    description: str
    github_urls: List[str]


class CVEIDProcessing(NamedTuple):
    need: bool
    github_urls: List[str]


class POCData(NamedTuple):
    cve_id: str
    description: str
    formatted_references: str


class POCObject(NamedTuple):
    description: str
    github_url: str


class RepositoryNameAndUserName(NamedTuple):
    user_name: str
    repository_name: str
