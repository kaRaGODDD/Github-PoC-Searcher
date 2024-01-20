from typing import NamedTuple
from datetime import datetime

class ExploitData(NamedTuple):
    cve_name: str
    description: str
    publishing_date: datetime
    url_to_github_repository: str
    
pattern_of_md_file = '''
# {}

## Description

{}

---

### Reference to GitHub Repository

- [GitHub Repository]({})

### Additional Information

- Published Date: {}
'''