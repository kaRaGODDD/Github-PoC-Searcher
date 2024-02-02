pattern_of_md_file = '''
# [{}]({})

## Description

- `{}`

## Cvss Data

- **Access Vector**:
  - {}
- **Base Score**:
  - {}

## Scores

- **Exploitability Score**:
  - {}
- **Impact Score**:
  - {}
- **Base Severity**:
  - {}

## Other Information

- **Publish Date**:
  - {}
- **Vulnerability Status**:
  - {}

## References

{}
'''

pattern_of_md_poc_file = '''
# [{}]({})

## Description

{}

## References

{}
'''

GRAPHQL_QUERY = '''
query {{
  rateLimit {{
      cost
      remaining
      resetAt
  }}
  search(query: "{}", type: REPOSITORY, first: 100) {{
    repositoryCount 
    edges {{
      node {{
        ... on Repository {{
          url
        }}
      }}
    }}
  }}
}}
'''