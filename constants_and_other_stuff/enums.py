from enum import Enum, auto

class POCSearchMethod(Enum):
    GITHUB_API_SEARCH = auto()
    GRAPHQL_SEARCH = auto()


class FileFormat(Enum):
    JSON = auto()
    MD = auto()


class DirectoryType(Enum):
    PROOF_OF_CONCEPT_DIRECTORY = auto()
    CVE_DATABASE_DIRECTORY = auto()


class ScrapingType(Enum):
    UPDATE = auto()
    SCRAPPING = auto()


class POCSearchType(Enum):
    TRAVERSE_ALL_CVE_DIRECTORIES = auto()
    TRAVERSE_FIX_YEAR_ON_CVE_DIRECTORY = auto()
    TRAVERSE_MULTIPLE_DIRECTORIES = auto()
