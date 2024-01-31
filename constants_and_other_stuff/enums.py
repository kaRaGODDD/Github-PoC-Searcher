from enum import Enum, auto

class POCChoiceSearch(Enum):
    GITHUB_API_SEARCH = auto()
    GRAPHQL_SEARCH = auto()


class FileSaving(Enum):
    JSON = auto()
    MD = auto()