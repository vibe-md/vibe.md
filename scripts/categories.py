"""Conservative, deterministic category suggestions for catalog packages."""
import re

CATEGORIES = (
    'Version Control', 'Testing', 'Debugging', 'Deployment', 'Documentation',
    'Security', 'Productivity', 'Database', 'Frontend', 'Backend', 'DevOps',
    'Performance', 'Accessibility', 'Monitoring', 'AI / Agents',
)

# These are suggestions, not a semantic classifier. Keep ambiguous text unclassified.
RULES = (
    ('Database', r'\b(?:database|schema migration|sql|postgres(?:ql)?|mysql)\b'),
    ('Security', r'\b(?:security|cybersecurity|credentials?|secrets?|api keys?|tokens?|vulnerabilit(?:y|ies)|authorization|authentication|access control)\b'),
    ('Frontend', r'\b(?:frontend|front-end|user interface|ui components?|css)\b'),
    ('Backend', r'\b(?:backend|back-end|server-side|rest api|graphql api)\b'),
    ('Testing', r'\b(?:unit tests?|integration tests?|test suite|test coverage|automated tests?|testing)\b'),
    ('Version Control', r'\b(?:git|github|gitlab|version control|pull requests?|git branches|git commits?)\b'),
    ('Deployment', r'\b(?:deploy(?:ment|ments|ing)?|release pipelines?)\b'),
    ('DevOps', r'\b(?:devops|ci/cd|continuous integration|infrastructure as code|kubernetes)\b'),
    ('Documentation', r'\b(?:documentation|markdown|technical writing|readability)\b'),
    ('Debugging', r'\b(?:debug(?:ging)?|troubleshoot(?:ing)?|diagnos(?:e|ing) (?:errors|bugs|failures))\b'),
    ('Performance', r'\b(?:performance|latency|profiling|optimization)\b'),
    ('Accessibility', r'\b(?:accessibility|a11y|screen readers?|wcag)\b'),
    ('Monitoring', r'\b(?:monitoring|observability|telemetry|metrics|alerting)\b'),
    ('AI / Agents', r'\b(?:large language models?|llms?|agent orchestration|prompt engineering|retrieval augmented generation|rag)\b'),
    ('Productivity', r'\b(?:productivity|task management|time management)\b'),
)


def infer_categories(description):
    text = description.lower()
    found = [category for category, pattern in RULES if re.search(pattern, text)]
    # Protecting database changes from destructive operations concerns data safety.
    if 'Database' in found and re.search(r'\b(?:destructive|data loss|reversible|rollback)\b', text):
        if 'Security' not in found:
            found.insert(1, 'Security')
    return found[:3]
