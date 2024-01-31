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