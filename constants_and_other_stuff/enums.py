from enum import Enum, auto

class POCChoiceSearch(Enum):
    GITHUB_API_SEARCH = auto()
    GRAPHQL_SEARCH = auto()


class FileSaving(Enum):
    JSON = auto()
    MD = auto()


class TypeOfTheDirectory(Enum):
    PROOF_OF_CONCEPT_DIRECTORY = auto()
    CVE_DATABASE_DIRECTORY = auto()


class TypeOfScrapping(Enum):
    UPDATE = auto()
    SCRAPPING = auto()

class TypeOfPOCSearching(Enum):
    TRAVERSE_ALL_CVE_DIRECTORY = auto()
    TRAVERSE_FIX_YEAR_ON_CVE_DIRECTORY = auto()
