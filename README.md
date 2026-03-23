# agent-md-validator

Validate [agent-md-specs](https://github.com/totalmarkdown/agent-md-specs)
configuration files.

[![License: CC0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Maintained by TotalMarkdown](https://img.shields.io/badge/maintained%20by-TotalMarkdown.ai-8B5CF6)](https://totalmarkdown.ai)

## What it validates

- **YAML frontmatter** — required fields (`spec_name`, `spec_version`,
  `category`, `tier`), valid tier/priority values, semver format
- **Core spec fields** — Core tier specs must also have `priority` and `domain`
- **Required sections** — key specs (SOUL.md, ESCALATION.md, LIMITS.md, etc.)
  are checked for expected `##` headings
- **Cross-references** — warns if a spec references another spec that
  doesn't exist in the bundle
- **Filename consistency** — `spec_name` must match the actual filename

## Installation

```bash
pip install agent-md-validator
```

Or install from source:

```bash
git clone https://github.com/totalmarkdown/agent-md-validator.git
cd agent-md-validator
pip install -e .
```

## Usage

```bash
# Validate a single spec file
agent-md-validate specs/identity/SOUL.md

# Validate an entire agent bundle directory
agent-md-validate ./my-agent/

# Strict mode — warnings become errors
agent-md-validate --strict ./my-agent/

# JSON output for CI/CD
agent-md-validate --format json ./my-agent/
```

## CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
name: Validate Agent Specs
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install agent-md-validator
      - run: agent-md-validate --strict ./specs/
```

## Output Formats

### Text (default)

```
specs/identity/SOUL.md
  ERROR   Missing required field: tier
  WARN    Missing recommended section: '## Values'

    Validation Summary
  Files checked    12
  Passed            9
  Errors            2
  Warnings          3
PASSED (with warnings)
```

### JSON (`--format json`)

```json
{
  "files_checked": 12,
  "passed": 9,
  "overall": "PASSED",
  "results": [
    {
      "path": "specs/identity/SOUL.md",
      "valid": false,
      "issues": [
        {"level": "error", "message": "Missing required field: tier"}
      ]
    }
  ]
}
```

## Spec Coverage

Frontmatter validation runs on all spec files. Section validation
currently covers these Core specs:

| Spec | Required Sections |
|------|-------------------|
| SOUL.md | Purpose, Personality, Values |
| ESCALATION.md | Levels, Triggers, Contacts |
| LIMITS.md | Hard Limits, Soft Limits |
| TEAM.md | Members, Coordination |
| WHOAMI.md | Identity, Verification |
| INPUT.md | Accepted Formats, Validation |
| OUTPUT.md | Output Formats, Schema |
| DELEGATION.md | Delegating Principal, Delegation Scope, Revocation |
| ATTESTATION.md | Attestation Method, Credential Lifecycle |
| AUDITTRAIL.md | Audit Event Schema, Tamper Resistance |
| SESSION.md | Session Identity, Session Boundaries, Destruction Policy |
| ENFORCEMENT.md | Pre-Deployment Validation, Runtime Enforcement Matrix |
| INTENT.md | Intent Declaration Format, Confidence Level |
| LEASTPRIVILEGE.md | Privilege Baseline, Just-In-Time Escalation |
| PROMPTSHIELD.md | Direct Injection Controls, Detection Methods |
| PROVENANCE.md | Input Source Registry, Contamination Policy |

All other specs receive frontmatter-only validation.

## License

[CC0 1.0 Universal](./LICENSE) — Public Domain.

---

Part of the [agent-md-specs](https://github.com/totalmarkdown/agent-md-specs) ecosystem.
Maintained by [TotalMarkdown.ai](https://totalmarkdown.ai).
