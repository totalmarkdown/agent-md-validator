"""Tests for agent-md-validator."""

from pathlib import Path

import pytest

from agent_md_validator.validator import (
    extract_headings,
    parse_frontmatter,
    validate_bundle,
    validate_file,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        content = "---\nname: test\nversion: 1.0\n---\n# Body"
        fm, body = parse_frontmatter(content)
        assert fm == {"name": "test", "version": 1.0}
        assert "# Body" in body

    def test_missing_frontmatter(self):
        content = "# No frontmatter here"
        fm, body = parse_frontmatter(content)
        assert fm is None

    def test_invalid_yaml(self):
        content = "---\n: invalid: yaml: [[\n---\n# Body"
        fm, body = parse_frontmatter(content)
        assert fm is None


class TestExtractHeadings:
    def test_extracts_h2_and_h3(self):
        body = "## First\ntext\n### Second\ntext\n## Third"
        headings = extract_headings(body)
        assert headings == ["First", "Second", "Third"]

    def test_ignores_h1(self):
        body = "# H1\n## H2"
        headings = extract_headings(body)
        assert headings == ["H2"]


class TestValidateFile:
    def test_valid_soul(self):
        result = validate_file(FIXTURES / "valid_soul.md")
        assert result.is_valid
        assert not result.has_errors

    def test_invalid_soul(self):
        result = validate_file(FIXTURES / "invalid_soul.md")
        errors = [i for i in result.issues if i.level == "error"]
        warnings = [i for i in result.issues if i.level == "warning"]
        # Should have errors for missing tier field
        assert any("tier" in i.message for i in errors)
        # Should have warnings for wrong name and bad version
        assert any("spec_name" in i.message for i in warnings)
        assert any("semver" in i.message.lower() or "version" in i.message.lower() for i in warnings)

    def test_nonexistent_file(self):
        result = validate_file(FIXTURES / "does_not_exist.md")
        assert result.has_errors


class TestValidateBundle:
    def test_valid_bundle(self):
        results = validate_bundle(FIXTURES / "valid_bundle")
        assert len(results) == 3
        assert all(r.is_valid for r in results)

    def test_cross_references(self):
        results = validate_bundle(FIXTURES / "valid_bundle")
        # TEAM.md references WHOAMI.md, which exists — no cross-ref warning
        team_result = [r for r in results if "TEAM.md" in r.path][0]
        cross_ref_issues = [
            i for i in team_result.issues if "Cross-references" in i.message
        ]
        assert len(cross_ref_issues) == 0
