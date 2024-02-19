from pydantic import BaseModel, Field
from typing import List, Optional


class _Item(BaseModel):
    html_url: str


class UrlFromResponse(BaseModel):
    total_count: int
    items: Optional[List[_Item]] = Field(None,alias='items')


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
    references: List[_Source]
    metrics: _Metrics


class _RepositoryQL(BaseModel):
    url: str


class _EdgeQL(BaseModel):
    node: _RepositoryQL


class _SearchQL(BaseModel):
    repositoryCount: int
    edges: List[_EdgeQL]


class _DataQL(BaseModel):
    search: _SearchQL


class GraphQLAnswerModel(BaseModel):
    data: _DataQL


class _Topic(BaseModel):
    name: Optional[str] = Field("", alias='name')


class _NodeTopic(BaseModel):
    topic: _Topic


class TopicContent(BaseModel):
    node: _NodeTopic


class _RepositoryTopics(BaseModel):
    edges: Optional[List[TopicContent]] = Field(None, alias='edges')


class _Node(BaseModel):
    name: str
    description: Optional[str] = Field(None, alias='description')
    url: Optional[str] = Field(None, alias='url')
    repositoryTopics: _RepositoryTopics


class RepositoryContent(BaseModel):
    node: _Node


class _Search(BaseModel):
    repositoryCount: int
    edges: Optional[List[RepositoryContent]] = Field(None, alias='edges')


class _Data(BaseModel):
    search: _Search


class FastSearchValidator(BaseModel):
    data: _Data
