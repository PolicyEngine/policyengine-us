"""The partner contract test rule and the files it relies on agree.

CLAUDE.md's "Partner API contract tests" section lets anyone update a partner
expected value when, among other conditions, the PR tags Ziming Hua and
`.github/workflows/partner-api-impact-notice.yaml` posts the change to Slack.
These checks keep that rule true to the repository: the workflow must exist,
watch the folder the rule names and list the PR's files in that folder. Both
AGENTS.md files summarize the rule and link to the CLAUDE.md section, and a
renamed heading would break those links without failing anything else.
"""

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
CLAUDE_MD = REPO / "CLAUDE.md"
PARTNERS = "policyengine_us/tests/policy/baseline/partners"
WORKFLOW_PATH = ".github/workflows/partner-api-impact-notice.yaml"
AGENTS_FILES = [REPO / "AGENTS.md", REPO / PARTNERS / "AGENTS.md"]
SECTION = "Partner API contract tests"
APPROVER = "hua7450"


def _slug(heading):
    """GitHub's anchor for a heading: lower case, punctuation dropped."""
    text = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return text.replace(" ", "-")


def _headings(text):
    """Anchors of the Markdown headings, skipping `#` lines in code blocks."""
    headings, fenced = set(), False
    for line in text.splitlines():
        if line.startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced and re.match(r"#{1,6} ", line):
            headings.add(_slug(line.lstrip("#")))
    return headings


def _section(text, title):
    """The text under `## <title>`, up to the next second-level heading."""
    match = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, f"CLAUDE.md has no '## {title}' section"
    return match.group(1)


def test_rule_names_the_folder_the_notice_workflow_and_the_approver():
    rule = _section(CLAUDE_MD.read_text(), SECTION)
    assert f"`{PARTNERS}/**`" in rule
    assert f"`{WORKFLOW_PATH}`" in rule
    assert APPROVER in rule
    assert (REPO / PARTNERS).is_dir()


def test_notice_workflow_watches_the_partner_folder():
    workflow = yaml.safe_load((REPO / WORKFLOW_PATH).read_text())
    # PyYAML reads a bare `on` key as True and a quoted one as "on".
    trigger = workflow.get(True, workflow.get("on"))["pull_request_target"]
    assert f"{PARTNERS}/**" in trigger["paths"]
    assert {"opened", "reopened", "synchronize", "ready_for_review"} <= set(
        trigger["types"]
    )
    steps = workflow["jobs"]["notify-slack"]["steps"]
    scripts = "\n".join(step.get("run", "") for step in steps)
    # The step that lists the PR's partner files filters on the same folder.
    # Only a plain or extended grep keeps the matching files: -v would drop
    # them and -c would count them, and either would silence the notice.
    assert re.search(rf"grep (?:-E )?'\^{re.escape(PARTNERS)}/'", scripts)
    assert any(
        "SLACK_PARTNER_WEBHOOK_URL" in str(step.get("env", {})) for step in steps
    )


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
