import os
import re
import sys
from github import Github

# Replace with your GitHub token (you'll set this as a secret later)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('GITHUB_REPOSITORY')

# A simple regex pattern to find bearer tokens (this is just an example)
TOKEN_PATTERN = r'(?<=Bearer\s)([A-Za-z0-9._-]+)'

def scan_for_tokens(directory):
    issues = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):  # Adjust as necessary
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    if re.search(TOKEN_PATTERN, content):
                        issues.append(f'Token found in {file}')
    return issues

def create_github_issue(title, body):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    repo.create_issue(title=title, body=body)

def main():
    issues = scan_for_tokens('.')
    if issues:
        body = '# Security Check Failed\n\n'
        body += 'The following issues were found:\n'
        for issue in issues:
            body += f'- {issue}\n'
        body += '\n**Suggestions:**\n- Ensure bearer tokens are not hardcoded and use environment variables instead.'
        create_github_issue("Security Issue Detected: Bearer Token Exposure", body)
        sys.exit(1)
    else:
        print("No issues found.")
        sys.exit(0)

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
