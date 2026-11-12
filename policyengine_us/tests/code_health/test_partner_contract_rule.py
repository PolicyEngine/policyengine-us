"""Keep source, review and CI safeguards consistent in partner-test guidance."""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CLAUDE_MD = REPO / "CLAUDE.md"
PARTNERS = "policyengine_us/tests/policy/baseline/partners"
AGENTS_FILES = [REPO / "AGENTS.md", REPO / PARTNERS / "AGENTS.md"]
SECTION = "Partner API contract tests"


def _slug(heading):
    """GitHub's anchor for a heading: lower case, punctuation dropped."""
    text = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return text.replace(" ", "-")


def _headings(text):
    """Read Markdown headings outside fenced code blocks."""
    headings, fence = set(), None
    for line in text.splitlines():
        match = re.match(r" {0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            run, rest = match.groups()
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not rest.strip():
                fence = None
        elif fence is None and re.match(r"#{1,6} ", line):
            headings.add(_slug(line.lstrip("#")))
    return headings


def _section(text, title):
    """Read one second-level section, stopping at the next heading."""
    matches = re.findall(
        rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", text, re.M | re.S
    )
    assert len(matches) == 1, f"Expected one '## {title}' section"
    return matches[0]


def test_all_partner_guidance_keeps_source_evidence_review_and_ci_guards():
    rule = _section(CLAUDE_MD.read_text(), SECTION)
    safeguards = (
        "one designated editor",
        "primary sources independently of the implementation",
        "file, case, variable, old value, new value and source justification",
        "every output variable of each affected case",
        "boundary cases, failing or not",
        "parameter trees and formula-derived thresholds at the base and head",
        "Preserve the pre-change failing results",
        "Check partner-flagged cases and any dependency a partner identified",
        "diff contains only the intended expectation, input, eligibility and coverage",
        "Do not delete, skip, rename or loosen a case merely to make CI pass",
        "independent automated review at the current head",
        "neither made the model change nor edited the expectations",
        "reviewer recomputes each changed value from the primary source",
        "all required CI checks at the current head",
    )
    for text in [rule, *(path.read_text() for path in AGENTS_FILES)]:
        for safeguard in safeguards:
            assert safeguard in text, safeguard
    assert f"`{PARTNERS}/**`" in rule
    assert (REPO / PARTNERS).is_dir()


def test_human_review_requires_a_material_expertise_question():
    rule = _section(CLAUDE_MD.read_text(), SECTION)
    for text in [rule, *(path.read_text() for path in AGENTS_FILES)]:
        assert "human review only for a specific material open question" in text
        assert "requires that person's expertise" in text
        assert "name the question in the request" in text
        assert (
            "Resolve any source conflict, untraced value or partner compatibility"
            in text
        )
        assert (
            "Do not request human review or notify a person to keep them informed"
            in text
        )
        assert "three-question" not in text
        assert "@-mention" not in text


def test_partner_edits_do_not_trigger_an_automatic_external_notice():
    assert not (REPO / ".github/workflows/partner-api-impact-notice.yaml").exists()


def test_agents_files_link_to_the_rule():
    headings = _headings(CLAUDE_MD.read_text())
    anchor = _slug(SECTION)
    assert anchor in headings
    for agents in AGENTS_FILES:
        targets = re.findall(r"\]\(([^)]*CLAUDE\.md#[^)]*)\)", agents.read_text())
        rule_links = [target for target in targets if target.endswith(f"#{anchor}")]
        assert rule_links, f"{agents.relative_to(REPO)} must link to the rule"
        for target in rule_links:
            path = target.split("#")[0]
            assert (agents.parent / path).resolve() == CLAUDE_MD, (agents, target)


def test_development_skills_load_without_a_permission_question():
    rule = _section(CLAUDE_MD.read_text(), "Development skills")
    assert "without asking whether to load them" in rule
    assert "policyengine-model-development" in rule
    assert "policyengine-standards" in rule
