"""Tie PolicyEngine-US code to the shared source-conflict register.

When a statute conflicts with a regulation, form, instructions, manual or
stated agency practice, PolicyEngine-US follows the statute; forms and
instructions fill gaps where the statute is silent. Each such choice is an
entry in the register PolicyEngine-US shares with Axiom
(``known-source-conflicts.yaml`` in TheAxiomFoundation/rulespec-us; field
reference in that repository's tools/README.md). The code that makes the
choice says so at the deciding line:

    # Source conflict us-hi:claim-of-right-deduction-floor

This test reads a vendored copy of the register, pinned by commit and sha256
(``source_conflicts/pin.yaml`` at the repository root; refresh it with
``scripts/update_source_conflicts.py``), so CI never depends on a moving
branch. Comments are read syntax-aware: Python comment tokens, and YAML
comments outside quoted and block scalars. Invariants, checked on every run:

1. The vendored copy is byte-identical to what its pin names (sha256), and
   the pin names rulespec-us at a full commit.
2. Every comment in policyengine_us/{variables,parameters,reforms} that
   starts like a marker ("# Source conflict ...", any spacing or case) is a
   well-formed marker on its own comment line, names a registered entry, and
   that entry lists the marker's file as a PolicyEngine/policyengine-us
   implementation.
3. Every PolicyEngine/policyengine-us implementation that the register says
   cites its entry (``cites_entry: true``) exists here and still carries its
   marker.
4. Ratchet: comments that read like a source conflict ("the instructions
   say", "in practice", "discrepancy", ...) in files with no marker may not
   change in number, file by file. A file with any valid marker is exempt, so
   the ratchet does not prove every conflict or deciding line in it is marked.
5. Backlog: ``source_conflicts/candidates.yaml`` lists every known conflict
   not yet registered. Each candidate has a well-formed, unique global id that
   is not yet in the register (registering one removes it from the backlog),
   valid kinds, states and years, https links, and code paths inside this
   repository that exist; the file's raw text, comments and keys included, is
   public (no decision-queue ids, session ids, local paths or email addresses).

These are structural checks: they tie markers, the register and the backlog
together; they do not judge whether code follows a statute. rulespec-us's own
``verify`` checks the other half at pinned commits: that each listed file and
test exists and that ``cites_entry`` is true.
"""

from __future__ import annotations

import hashlib
import io
import re
import tokenize
from collections import Counter
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
FOLDER = REPO_ROOT / "source_conflicts"
REGISTER = FOLDER / "known-source-conflicts.yaml"
PIN = FOLDER / "pin.yaml"
CANDIDATES = FOLDER / "candidates.yaml"
THIS_REPO = "PolicyEngine/policyengine-us"
SCANNED = (
    "policyengine_us/variables",
    "policyengine_us/parameters",
    "policyengine_us/reforms",
)

GLOBAL_ID = r"[a-z]{2}(?:-[a-z0-9]+)*:[a-z0-9]+(?:-[a-z0-9]+)*"
# The one spelling of a marker, alone on its comment line.
MARKER_RE = re.compile(rf"# Source conflict ({GLOBAL_ID})")
# A comment that starts like a marker, in any case or spacing; prose such as
# "Source conflict: the plan says ..." is not one, and counts toward the
# ratchet below instead.
ATTEMPT_RE = re.compile(r"#\s*source\s+conflict(?![\w:])(?!\s*:)", re.IGNORECASE)

# Comment lines that read like a disagreement between sources.
CONFLICT_COMMENT_RE = re.compile(
    r"""(?ix)
      discrepanc
    | \bsource\ conflict\b
    | \bcontrary\ to\b
    | \bdepart(s|ed|ing)?\ from\b
    | \b(law|statute|statutory\ text|code|regulation|rule)\s+(says|said|states|provides)\b.{0,80}\b(but|while|whereas|however)\b
    | \b(form|instructions?|worksheet|booklet|manual|guidance|calculator)\s+(says|say|said|states|state|uses|use|tells?)\b
    | \bin\ practice\b
    | \bconflicts?\ with\b
    | \binconsistent\ with\b
    | \bwe\ (apply|follow|use)\s+(the\ )?(form|instructions?|worksheet|booklet|manual)\b
    | \brather\ than\ the\ (statute|law|form|instructions?)\b
    | \b(statute|law)\s+is\s+silent\b
    """
)

# Files with conflict-sounding comments and no marker, and how many such
# lines each has. A file may only go down: register and mark the conflict,
# or reword a comment that is not one, then lower or delete its count here.
# A new file or a higher count fails.
KNOWN_UNMARKED: dict[str, int] = {
    "policyengine_us/parameters/gov/irs/credits/residential_clean_energy/fuel_cell_cap_per_kw.yaml": 1,
    "policyengine_us/parameters/gov/irs/income/exemption/overtime/hce_salary_threshold.yaml": 1,
    "policyengine_us/parameters/gov/irs/income/exemption/overtime/salary_basis_threshold.yaml": 1,
    "policyengine_us/parameters/gov/ssa/ssi/income/ism/food_counts.yaml": 1,
    "policyengine_us/parameters/gov/states/ar/ade/oec/sra/rates/no_copay_smi_threshold.yaml": 1,
    "policyengine_us/parameters/gov/states/ca/cpuc/income_sources.yaml": 1,
    "policyengine_us/parameters/gov/states/co/doi/premium_assistance/amount/additional_member.yaml": 1,
    "policyengine_us/parameters/gov/states/co/doi/premium_assistance/amount/first_member.yaml": 1,
    "policyengine_us/parameters/gov/states/hi/bessd/ccap/income/countable_income/sources.yaml": 1,
    "policyengine_us/parameters/gov/states/ma/hic/connector_care/fpl_floor.yaml": 1,
    "policyengine_us/parameters/gov/states/mo/tax/income/deductions/federal_income_tax/ignored_credits.yaml": 1,
    "policyengine_us/parameters/gov/states/mt/tax/income/subtractions/disability_income/cap.yaml": 1,
    "policyengine_us/parameters/gov/states/or/ohcs/liheap/payment/income_band.yaml": 1,
    "policyengine_us/parameters/gov/states/ut/dwf/ccap/copay/income_limits.yaml": 1,
    "policyengine_us/parameters/gov/states/wi/tax/income/credits/homestead/income/disqualified_loss_sources.yaml": 1,
    "policyengine_us/parameters/gov/territories/pr/tax/income/credits/earned_income/eligibility/min.yaml": 1,
    "policyengine_us/parameters/gov/territories/pr/tax/income/credits/earned_income/eligibility/separate_filer.yaml": 1,
    "policyengine_us/parameters/gov/territories/pr/tax/income/credits/earned_income/max_amount.yaml": 1,
    "policyengine_us/parameters/gov/territories/pr/tax/income/credits/earned_income/phase_in_rate.yaml": 1,
    "policyengine_us/parameters/gov/territories/pr/tax/income/credits/earned_income/phase_out/rate.yaml": 1,
    "policyengine_us/parameters/gov/territories/pr/tax/income/credits/earned_income/phase_out/threshold/joint.yaml": 1,
    "policyengine_us/parameters/gov/territories/pr/tax/income/credits/earned_income/phase_out/threshold/single.yaml": 1,
    "policyengine_us/parameters/gov/territories/pr/tax/income/credits/earned_income/unearned_income/limit.yaml": 1,
    "policyengine_us/parameters/gov/territories/pr/tax/income/gradual_adjustment/exemption_rate.yaml": 1,
    "policyengine_us/parameters/gov/territories/pr/tax/income/gradual_adjustment/threshold.yaml": 1,
    "policyengine_us/parameters/gov/usda/snap/eligibility/waiting_period/subject_immigration_statuses.yaml": 1,
    "policyengine_us/reforms/states/az/dependent_credit/az_dependent_credit_reform.py": 1,
    "policyengine_us/reforms/states/mn/walz/mn_walz_hf1938.py": 1,
    "policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/section_199a_net_capital_gain.py": 2,
    "policyengine_us/variables/gov/local/ca/cc/ga/ca_cc_general_assistance_maximum_grant.py": 1,
    "policyengine_us/variables/gov/local/ca/cc/ga/eligibility/ca_cc_general_assistance_eligible.py": 1,
    "policyengine_us/variables/gov/local/tax/sales/local_sales_tax.py": 1,
    "policyengine_us/variables/gov/states/ar/ade/oec/sra/rates/ar_sra_daily_copay.py": 1,
    "policyengine_us/variables/gov/states/ct/tax/income/rebate/ct_child_tax_rebate.py": 1,
    "policyengine_us/variables/gov/states/hi/tax/income/credits/cdcc/hi_cdcc_qualifying_individuals.py": 1,
    "policyengine_us/variables/gov/states/hi/tax/income/subtractions/hi_student_loan_interest_adjustment.py": 1,
    "policyengine_us/variables/gov/states/ks/tax/income/deductions/ks_itemized_deductions.py": 1,
    "policyengine_us/variables/gov/states/ky/dcbs/liheap/ky_liheap.py": 1,
    "policyengine_us/variables/gov/states/mn/dcyf/mfip/income/earned/mn_mfip_dependent_care_deduction.py": 1,
    "policyengine_us/variables/gov/states/mn/tax/income/deductions/mn_itemized_deductions.py": 1,
    "policyengine_us/variables/gov/states/mn/tax/income/subtractions/mn_k12_education_subtraction.py": 1,
    "policyengine_us/variables/gov/states/mo/dese/ccs/eligibility/mo_ccs_income_eligible.py": 1,
    "policyengine_us/variables/gov/states/vt/tax/income/credits/cdcc/vt_low_income_cdcc_eligible.py": 1,
    "policyengine_us/variables/gov/states/wa/dor/property_tax_exemption/senior_disabled/wa_pte_categorical_eligible.py": 1,
    "policyengine_us/variables/gov/territories/pr/tax/income/pr_agi.py": 1,
}


def _code_files():
    for root in SCANNED:
        for path in sorted((REPO_ROOT / root).rglob("*")):
            if path.suffix in (".py", ".yaml") and path.is_file():
                yield path


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _python_comments(text: str):
    """(line, comment, inline) for each comment token; inline means code
    precedes it on its line. Strings that look like comments are not tokens."""

    lines = text.splitlines()
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                row, col = token.start
                inline = bool(lines[row - 1][:col].strip())
                yield row, token.string.strip(), inline
    except (tokenize.TokenError, SyntaxError, IndentationError):
        return


BLOCK_SCALAR_RE = re.compile(
    r"^(\s*)(?:-\s+)?(?:[^#\s][^#]*:\s+)?[|>][-+0-9]*\s*(?:#.*)?$"
)


def _yaml_comments(text: str):
    """(line, comment, inline) for each YAML comment outside quoted and block
    scalars (a `#` starts a comment at a line's start or after whitespace)."""

    block_indent = None
    for number, line in enumerate(text.splitlines(), 1):
        indent = len(line) - len(line.lstrip())
        if block_indent is not None:
            if not line.strip() or indent > block_indent:
                continue  # inside a | or > block scalar
            block_indent = None
        if line.lstrip().startswith("#"):
            yield number, line.strip(), False
            continue
        quote = None
        for index, char in enumerate(line):
            if quote:
                if char == quote:
                    quote = None
            elif char in "'\"" and (index == 0 or line[index - 1] in " :[{,-"):
                quote = char
            elif char == "#" and index > 0 and line[index - 1] in " \t":
                yield number, line[index:].strip(), True
                break
        if BLOCK_SCALAR_RE.match(line):
            block_indent = indent


def _comments(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".py":
        return list(_python_comments(text))
    return list(_yaml_comments(text))


def _load():
    payload = yaml.safe_load(REGISTER.read_text(encoding="utf-8"))
    entries = {}
    for entry in payload["entries"]:
        entries[f"{entry['jurisdiction']}:{entry['id']}"] = entry
    return payload, entries


def _our_implementations(entry):
    return [
        item
        for item in entry.get("implementations") or []
        if item.get("repo") == THIS_REPO
    ]


def _markers():
    found = []  # (global id, relative path, line number)
    malformed = []
    for path in _code_files():
        for number, comment, inline in _comments(path):
            if not ATTEMPT_RE.match(comment):
                continue
            match = MARKER_RE.fullmatch(comment)
            if match is None or inline:
                malformed.append(f"{_relative(path)}:{number}: {comment}")
            else:
                found.append((match.group(1), _relative(path), number))
    return found, malformed


def test_vendored_register_matches_its_pin():
    pin = yaml.safe_load(PIN.read_text(encoding="utf-8"))
    assert pin["repo"] == "TheAxiomFoundation/rulespec-us"
    assert pin["path"] == "known-source-conflicts.yaml"
    assert re.fullmatch(r"[0-9a-f]{40}", pin["commit"])
    assert hashlib.sha256(REGISTER.read_bytes()).hexdigest() == pin["sha256"], (
        "The vendored register differs from its pin. Refresh both with "
        "`python scripts/update_source_conflicts.py --commit <rulespec-us commit>`; "
        "never edit the copy by hand."
    )


def test_vendored_register_has_unique_global_ids():
    payload, entries = _load()
    assert payload["version"] == 1
    assert len(entries) == len(payload["entries"])


def test_markers_are_well_formed():
    _, malformed = _markers()
    assert not malformed, (
        "Write a source-conflict marker exactly as `# Source conflict <jurisdiction>:<id>`, "
        "with single spaces, alone on its own comment line (not after code):\n"
        + "\n".join(malformed)
    )


def test_every_marker_names_a_registered_entry_that_lists_its_file():
    _, entries = _load()
    markers, _ = _markers()
    problems = []
    for global_id, path, number in markers:
        entry = entries.get(global_id)
        if entry is None:
            problems.append(
                f"{path}:{number}: {global_id} is not in the vendored register. Add the entry to "
                "rulespec-us known-source-conflicts.yaml first, then bump the pin."
            )
        elif path not in {item.get("path") for item in _our_implementations(entry)}:
            problems.append(
                f"{path}:{number}: {global_id} does not list {path} as a {THIS_REPO} implementation."
            )
    assert not problems, "\n".join(problems)


def test_registered_implementations_carry_their_marker():
    _, entries = _load()
    markers, _ = _markers()
    marked = {(global_id, path) for global_id, path, _ in markers}
    problems = []
    for global_id, entry in entries.items():
        for item in _our_implementations(entry):
            if not item.get("cites_entry"):
                continue  # not merged here yet, or not marked yet: verify reports it upstream
            path = item["path"]
            if not (REPO_ROOT / path).is_file():
                problems.append(
                    f"{global_id}: {path} no longer exists; update the register's implementation."
                )
            elif (global_id, path) not in marked:
                problems.append(
                    f"{global_id}: {path} has lost its `# Source conflict {global_id}` marker."
                )
    assert not problems, "\n".join(problems)


def _unmarked_conflict_comments() -> Counter:
    counts: Counter = Counter()
    for path in _code_files():
        comments = _comments(path)
        if any(
            MARKER_RE.fullmatch(comment) and not inline
            for _, comment, inline in comments
        ):
            continue
        for _, comment, _ in comments:
            if CONFLICT_COMMENT_RE.search(comment):
                counts[_relative(path)] += 1
    return counts


def test_conflict_sounding_comments_do_not_grow():
    counts = _unmarked_conflict_comments()
    grown = {
        path: count
        for path, count in counts.items()
        if count > KNOWN_UNMARKED.get(path, 0)
    }
    shrunk = {
        path: count
        for path, count in KNOWN_UNMARKED.items()
        if counts.get(path, 0) < count
    }
    assert not grown, (
        "These files gained comments that read like a conflict between sources, with no "
        "`# Source conflict <id>` marker. If a statute and a form, instructions, manual or "
        "agency practice disagree, register it (rulespec-us known-source-conflicts.yaml) and "
        f"mark the deciding line; otherwise reword the comment. Files and counts: {grown}"
    )
    assert not shrunk, (
        "These files now have fewer unmarked conflict-sounding comments; lower or delete "
        f"their KNOWN_UNMARKED counts to: { {path: counts.get(path, 0) for path in shrunk} }"
    )


@pytest.mark.parametrize(
    ("comment", "matches"),
    [
        (
            '# Law says "less than" but tax form says "$x or less". We apply form rules.',
            True,
        ),
        ("# The line 11j instructions say to consider each business", True),
        ("# In practice the change takes effect in 2025, not October 2024.", True),
        ("# discrepancy: legal statute doesn't include minimum age", True),
        ("# Hawaii's count departs from the federal one", True),
        ("# Source conflict: CCDF State Plan 2.3.1(b) describes a waiver", True),
        ("# Sum the head's and spouse's wages.", False),
        ("# See 26 USC 32(c)(2).", False),
    ],
)
def test_conflict_comment_pattern(comment, matches):
    assert bool(CONFLICT_COMMENT_RE.search(comment)) == matches


def test_marker_pattern():
    assert MARKER_RE.fullmatch("# Source conflict us-hi:claim-of-right-deduction-floor")
    assert not ATTEMPT_RE.match("# Source conflict: the plan and the manual disagree")
    assert not ATTEMPT_RE.match("# Source conflicts are registered in rulespec-us")
    for bad in (
        "# Source conflict us-hi",
        "# Source conflict US-HI:x",
        "# Source conflict us-hi:Bad_Id",
        "# Source conflict us-hi:x see the register",
        "# Source  conflict us-hi:missing",
        "# Source\tconflict us-hi:missing",
        "#Source conflict us-hi:missing",
        "# source conflict us-hi:missing",
    ):
        assert ATTEMPT_RE.match(bad) and not MARKER_RE.fullmatch(bad), bad


def test_comments_are_read_syntax_aware():
    python = (
        'DOC = """\n# Source conflict us-hi:inside-a-string\n"""\n'
        "x = 1  # Source conflict us-hi:inline\n"
        "# Source conflict us-hi:own-line\n"
    )
    assert [(n, c, i) for n, c, i in _python_comments(python)] == [
        (4, "# Source conflict us-hi:inline", True),
        (5, "# Source conflict us-hi:own-line", False),
    ]
    yaml_text = (
        "description: |\n"
        "  # Source conflict us-hi:inside-a-block-scalar\n"
        "  more text\n"
        "values:\n"
        "  2024-01-01: 1 # Source conflict us-hi:inline\n"
        "  title: 'a # not a comment'\n"
        "# Source conflict us-hi:own-line\n"
    )
    assert [(n, c, i) for n, c, i in _yaml_comments(yaml_text)] == [
        (5, "# Source conflict us-hi:inline", True),
        (7, "# Source conflict us-hi:own-line", False),
    ]


@pytest.mark.parametrize(
    ("years", "ok"),
    [
        ({"from": 2022, "to": 2025, "type": "tax"}, True),
        ({"from": 2024, "type": "calendar"}, True),
        ({"type": "tax"}, False),
        ({"from": "2022", "type": "tax"}, False),
        ({"from": 2025, "to": 2022, "type": "tax"}, False),
        ({"from": 2025, "type": "program"}, False),
        ({"from": 2025, "type": "tax", "until": 2026}, False),
        ("2022-2025", False),
    ],
)
def test_year_rules(years, ok):
    assert (_year_problems(years) == []) == ok


@pytest.mark.parametrize(
    ("path", "ok"),
    [
        ("policyengine_us/tests/code_health/test_source_conflicts.py", True),
        ("/etc/passwd", False),
        ("../outside.py", False),
        ("policyengine_us/../../outside.py", False),
        ("policyengine_us/no_such_file.py", False),
        ("", False),
        (None, False),
    ],
)
def test_code_paths_must_be_files_in_this_repository(path, ok):
    assert _inside_repository(path) == ok


# ---------------------------------------------------------------------------
# The backlog of known conflicts not yet registered

SOURCE_KINDS = {
    "statute",
    "regulation",
    "rulemaking",
    "form",
    "instructions",
    "worksheet",
    "manual",
    "guidance",
    "policy",
    "plan",
    "calculator",
    "agency-practice",
}
FOLLOWS = {"statute", "conflicting-source", "gap-fill", "not-modelled", "unknown"}
STATES = {"ruled", "open", "unreviewed"}
YEAR_TYPES = {"calendar", "tax", "federal-fiscal", "state-fiscal", "program"}
PRIVATE = (
    (re.compile(r"\bd[0-9]{3,5}\b"), "a decision-queue id"),
    (re.compile(r"\blocal_[0-9a-f]{8}"), "a session id"),
    (re.compile(r"(?:/Users/|/home/|/private/tmp|(?<![\w.])~/)"), "a local path"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[A-Za-z][\w.-]*"), "an email address"),
)


def _candidates():
    return yaml.safe_load(CANDIDATES.read_text(encoding="utf-8"))["candidates"]


def _strings(value, label):
    if isinstance(value, str):
        yield label, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _strings(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _strings(item, f"{label}[{index}]")


def test_candidates_have_unique_well_formed_ids():
    ids = [item["id"] for item in _candidates()]
    assert all(re.fullmatch(GLOBAL_ID, global_id) for global_id in ids), ids
    duplicated = sorted(
        global_id for global_id, count in Counter(ids).items() if count > 1
    )
    assert not duplicated, duplicated


def test_candidates_are_not_yet_registered():
    _, entries = _load()
    registered = sorted(set(entries) & {item["id"] for item in _candidates()})
    assert not registered, (
        f"These are registered now; delete them from candidates.yaml: {registered}"
    )


def test_candidate_fields():
    problems = []
    for item in _candidates():
        label = item.get("id")
        for key in ("id", "program", "question", "sources", "pe_us", "state"):
            if key not in item:
                problems.append(f"{label}: {key} is required")
        if item.get("state") not in STATES:
            problems.append(f"{label}: state must be one of {sorted(STATES)}")
        pe_us = item.get("pe_us") or {}
        if pe_us.get("follows") not in FOLLOWS:
            problems.append(f"{label}: pe_us.follows must be one of {sorted(FOLLOWS)}")
        years = item.get("years")
        if years is not None:
            problems.extend(f"{label}: {problem}" for problem in _year_problems(years))
        sources = item.get("sources") or []
        if len(sources) < 2:
            problems.append(f"{label}: a conflict needs at least two sources")
        for source in sources:
            if source.get("kind") not in SOURCE_KINDS:
                problems.append(
                    f"{label}: source kind {source.get('kind')!r} is not one of {sorted(SOURCE_KINDS)}"
                )
            url = source.get("url")
            if url is not None and not str(url).startswith("https://"):
                problems.append(f"{label}: source url must be https or null: {url}")
        for path in pe_us.get("code") or []:
            if not _inside_repository(path):
                problems.append(
                    f"{label}: code path {path!r} must be a relative path to a file in this repository"
                )
        for pr in pe_us.get("prs") or []:
            if not re.fullmatch(
                r"https://github\.com/PolicyEngine/policyengine-us/pull/[0-9]+", pr
            ):
                problems.append(
                    f"{label}: prs must be PolicyEngine/policyengine-us pull request URLs: {pr}"
                )
    assert not problems, "\n".join(problems)


def _year_problems(years) -> list[str]:
    if not isinstance(years, dict):
        return [
            "years must be a mapping of from, optional to, type and (for program) note"
        ]
    problems = []
    start, end = years.get("from"), years.get("to")
    if type(start) is not int:
        problems.append("years.from must be a whole year")
    if "to" in years and type(end) is not int:
        problems.append("years.to must be a whole year")
    if type(start) is int and type(end) is int and end < start:
        problems.append(f"years.to ({end}) is before years.from ({start})")
    if years.get("type") not in YEAR_TYPES:
        problems.append(f"years.type must be one of {sorted(YEAR_TYPES)}")
    if years.get("type") == "program" and not years.get("note"):
        problems.append("years.note must say what the program year is")
    unknown = set(years) - {"from", "to", "type", "note"}
    if unknown:
        problems.append(f"years has unknown keys {sorted(unknown)}")
    return problems


def _inside_repository(path) -> bool:
    if (
        not isinstance(path, str)
        or not path
        or Path(path).is_absolute()
        or ".." in Path(path).parts
    ):
        return False
    target = (REPO_ROOT / path).resolve()
    return target.is_relative_to(REPO_ROOT) and target.is_file()


def test_candidates_are_public():
    # The raw text, so comments and mapping keys are covered too.
    problems = [
        f"candidates.yaml:{number} contains {what}"
        for number, line in enumerate(
            CANDIDATES.read_text(encoding="utf-8").splitlines(), 1
        )
        for pattern, what in PRIVATE
        if pattern.search(line)
    ]
    assert not problems, "\n".join(problems)
