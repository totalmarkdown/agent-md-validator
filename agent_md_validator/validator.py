"""Core validation logic for agent-md-specs files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .schemas import (
    COMMON_CROSS_REFS,
    REQUIRED_FIELDS_ALL,
    REQUIRED_FIELDS_CORE,
    REQUIRED_SECTIONS,
    VALID_PRIORITIES,
    VALID_TIERS,
)


@dataclass
class Issue:
    path: str
    level: str  # "error" or "warning"
    message: str


@dataclass
class ValidationResult:
    path: str
    issues: list[Issue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.level == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.level == "warning" for i in self.issues)

    @property
    def is_valid(self) -> bool:
        return not self.has_errors


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Extract YAML frontmatter and body from markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return None, content
    try:
        fm = yaml.safe_load(match.group(1))
        return fm if isinstance(fm, dict) else None, match.group(2)
    except yaml.YAMLError:
        return None, content


def extract_headings(body: str) -> list[str]:
    """Extract all ## and ### level headings from markdown body."""
    return [
        m.group(1).strip()
        for m in re.finditer(r"^#{2,3}\s+(.+)$", body, re.MULTILINE)
    ]


def validate_file(path: Path) -> ValidationResult:
    """Validate a single spec file."""
    result = ValidationResult(path=str(path))
    rel = path.name

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        result.issues.append(Issue(str(path), "error", f"Cannot read file: {e}"))
        return result

    # Parse frontmatter
    frontmatter, body = parse_frontmatter(content)
    if frontmatter is None:
        result.issues.append(
            Issue(str(path), "error", "Missing or invalid YAML frontmatter")
        )
        return result

    # Check required fields (all specs)
    for field_name in REQUIRED_FIELDS_ALL:
        if field_name not in frontmatter:
            result.issues.append(
                Issue(str(path), "error", f"Missing required field: {field_name}")
            )

    # Validate tier value
    tier = frontmatter.get("tier", "")
    if tier and tier not in VALID_TIERS:
        result.issues.append(
            Issue(
                str(path),
                "error",
                f"Invalid tier '{tier}' — must be 'core' or 'extended'",
            )
        )

    # Core tier: check additional required fields
    if tier == "core":
        for field_name in REQUIRED_FIELDS_CORE:
            if field_name not in frontmatter:
                result.issues.append(
                    Issue(
                        str(path),
                        "error",
                        f"Core spec missing required field: {field_name}",
                    )
                )

    # Validate priority value
    priority = frontmatter.get("priority", "")
    if priority and str(priority).lower() not in VALID_PRIORITIES:
        result.issues.append(
            Issue(
                str(path),
                "warning",
                f"Non-standard priority '{priority}' — expected: {', '.join(sorted(VALID_PRIORITIES))}",
            )
        )

    # Validate version format
    version = frontmatter.get("spec_version", "")
    if version and not re.match(r"^\d+\.\d+\.\d+$", str(version)):
        result.issues.append(
            Issue(
                str(path),
                "warning",
                f"Version '{version}' is not valid semver (expected X.Y.Z)",
            )
        )

    # Check spec_name matches filename
    spec_name = frontmatter.get("spec_name", "")
    if spec_name and spec_name != rel:
        result.issues.append(
            Issue(
                str(path),
                "warning",
                f"spec_name '{spec_name}' does not match filename '{rel}'",
            )
        )

    # Check required sections
    if rel in REQUIRED_SECTIONS:
        headings = extract_headings(body)
        heading_lower = [h.lower() for h in headings]
        for section in REQUIRED_SECTIONS[rel]:
            if section.lower() not in heading_lower:
                result.issues.append(
                    Issue(
                        str(path),
                        "warning",
                        f"Missing recommended section: '## {section}'",
                    )
                )

    # Check footer
    if "agent-md-specs" not in body and "totalmarkdown" not in body.lower():
        result.issues.append(
            Issue(str(path), "warning", "Missing standard footer reference")
        )

    return result


def validate_bundle(directory: Path) -> list[ValidationResult]:
    """Validate all .md spec files in a directory."""
    results = []
    md_files = sorted(directory.rglob("*.md"))

    # Filter out README, INDEX, CONTRIBUTING, etc.
    spec_files = [
        f
        for f in md_files
        if f.name.isupper() or (f.name[0].isupper() and f.name != "README.md")
    ]

    if not spec_files:
        # Fall back to all .md files except common non-spec files
        skip = {"README.md", "INDEX.md", "CONTRIBUTING.md", "GOVERNANCE.md"}
        spec_files = [f for f in md_files if f.name not in skip]

    for spec_file in spec_files:
        results.append(validate_file(spec_file))

    # Cross-reference checks
    existing_specs = {f.name for f in spec_files}
    for spec_file in spec_files:
        if spec_file.name in COMMON_CROSS_REFS:
            for ref in COMMON_CROSS_REFS[spec_file.name]:
                if ref not in existing_specs:
                    for r in results:
                        if r.path == str(spec_file):
                            r.issues.append(
                                Issue(
                                    str(spec_file),
                                    "warning",
                                    f"Cross-references {ref} but it was not found in the bundle",
                                )
                            )

    return results
