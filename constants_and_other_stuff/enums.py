from enum import Enum, auto


class POCSearchMethod(Enum):
    GITHUB_API_SEARCH = auto()
    GRAPHQL_SEARCH = auto()


class FileFormat(Enum):
    JSON = auto()
    MD = auto()


class DirectoryType(Enum):
    POC_DIRECTORY = auto()
    CVE_DATABASE_DIRECTORY = auto()


class ScrapingType(Enum):
    UPDATE = auto()
    SCRAPING = auto()


class POCSearchType(Enum):
    TRAVERSE_ALL_CVE_DIRECTORIES_CONSISTENTLY = auto()
    TRAVERSE_FIX_YEAR_ON_CVE_DIRECTORY = auto()
    TRAVERSE_ALL_DIRECTORIES_AT_ONCE = auto()
    

class CveIDFromDifferentSources(Enum):
    FROM_REPOSITORY_NAME = auto()
    FROM_DESCRIPTION = auto()
    FROM_TOPICS = auto()


class Sources(Enum):
    GITHUB = auto()
    NVD = auto()