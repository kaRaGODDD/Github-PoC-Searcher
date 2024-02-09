CVE_FILE_TEMPLATE = '''
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

POC_FILE_TEMPLATE = '''
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

GRAPHQL_QUERY_FOR_FAST_INTERVAL_SEACH = '''
query {{
  search(query: "cve created:{}..{}", type: REPOSITORY, first: 100) {{
    repositoryCount
    edges {{
      node {{
        ... on Repository {{
          name
          description
          url
          repositoryTopics(first: 100) {{
            edges {{
              node {{
                topic {{
                  name
                }}
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
'''


MITRE_URL = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}"
