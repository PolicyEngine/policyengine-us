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
(``source_conflicts/pin.yaml``; refresh it with
``scripts/update_source_conflicts.py``), so CI never depends on a moving
branch. Invariants, checked on every run:

1. The vendored copy is byte-identical to what its pin names (sha256), and
   the pin names rulespec-us at a full commit.
2. Every marker in policyengine_us/{variables,parameters,reforms} is well
   formed and names a registered entry, and that entry lists the marker's
   file as a PolicyEngine/policyengine-us implementation.
3. Every PolicyEngine/policyengine-us implementation the register says cites
   its entry (``cites_entry: true``) exists here and still carries the marker.
4. Ratchet: comments that read like a source conflict ("the instructions
   say", "in practice", "discrepancy", ...) in files with no marker may not
   grow, file by file. Register the conflict and mark the line, or explain
   in review why the comment is not one, and update KNOWN_UNMARKED.

rulespec-us's own daily ``verify`` checks the other half at pinned commits:
that each listed file and test exists and that ``cites_entry`` is true.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
FOLDER = Path(__file__).resolve().parent / "source_conflicts"
REGISTER = FOLDER / "known-source-conflicts.yaml"
PIN = FOLDER / "pin.yaml"
THIS_REPO = "PolicyEngine/policyengine-us"
SCANNED = (
    "policyengine_us/variables",
    "policyengine_us/parameters",
    "policyengine_us/reforms",
)

GLOBAL_ID = r"[a-z]{2}(?:-[a-z0-9]+)*:[a-z0-9]+(?:-[a-z0-9]+)*"
MARKER_RE = re.compile(rf"#\s*Source conflict ({GLOBAL_ID})\s*$")
# A comment that starts like a marker; prose such as "Source conflict: the
# plan says ..." is not one, and counts toward the ratchet below instead.
ATTEMPT_RE = re.compile(r"#\s*source conflict\s+[^:\s]", re.IGNORECASE)

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


def _comment_lines(path: Path):
    for number, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        stripped = line.strip()
        if stripped.startswith("#"):
            yield number, stripped


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
        for number, comment in _comment_lines(path):
            if not ATTEMPT_RE.match(comment):
                continue
            match = MARKER_RE.fullmatch(comment)
            if match is None:
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
        "alone on its comment line:\n" + "\n".join(malformed)
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
        lines = list(_comment_lines(path))
        if any(MARKER_RE.fullmatch(comment) for _, comment in lines):
            continue
        for _, comment in lines:
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
    assert MARKER_RE.fullmatch("#Source conflict us:oasdi-family-maximum-saving-clause")
    assert not ATTEMPT_RE.match("# Source conflict: the plan and the manual disagree")
    for bad in (
        "# Source conflict us-hi",
        "# Source conflict US-HI:x",
        "# Source conflict us-hi:Bad_Id",
        "# Source conflict us-hi:x see the register",
    ):
        assert ATTEMPT_RE.match(bad) and not MARKER_RE.fullmatch(bad), bad
