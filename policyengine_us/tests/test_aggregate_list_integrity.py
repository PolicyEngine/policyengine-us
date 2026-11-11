"""Structural guards for benefit aggregate lists.

The first half covers the state-summing aggregate list parameters, which sum
implemented per-state variables into national aggregates. Three failure modes
have shipped before (see issues #9234 and #9080):
1. A list member that is not a defined variable (silent typo or rename).
2. A member without a state gate, leaking one state's program into every
   state (the dc_ctc bug).
3. A new year block silently dropping members of the previous block, since
   these lists are full-replacement rather than incremental.

The second half covers the benefit aggregates themselves. Structural reforms
used to replace household_benefits or spm_unit_benefits with their own
hardcoded copy of the list, and every copy fell behind: the Trump dividend
(#9430) and dozens of state SSI supplements reached the baseline lists only, so
those reforms dropped them for every household (#10226). Both lists are now
parameters, and a reform adds its own programs to them with
add_to_list_parameter. These tests keep it that way. No reform may redefine a
benefit total: household_benefits, spm_unit_benefits, or a variable that sums
a list feeding them, at any depth. Every reform that names one of those totals
or lists must appear in test_reform_benefit_lists.py, which fails when a
reform changes any list parameter beyond its own additions, or neutralizes or
redefines a benefit total.

The last test keeps reforms from copying the household tax totals at all. The
abolish-federal-income-tax and abolish-payroll-tax reforms once did, from a
separate list that lost the Idaho permanent building fund tax, five states'
use taxes and every local tax except New York City's.
"""

import ast
import re
from pathlib import Path

import pytest
import yaml

PACKAGE = Path(__file__).parent.parent
PARAMETERS = PACKAGE / "parameters"

AGGREGATE_LISTS = [
    "gov/states/household/state_ctcs.yaml",
    "gov/states/household/state_eitcs.yaml",
    "gov/states/household/state_cdccs.yaml",
    "gov/hhs/ccdf/child_care_subsidy_programs.yaml",
    "gov/household/household_state_benefits.yaml",
    "gov/states/household/state_property_tax_refunds.yaml",
]

# Gates that restrict a variable geographically without a StateCode
# defined_for (locality booleans).
GEOGRAPHIC_GATES = {"in_la", "in_nyc", "in_riv"}

# Variables that cap an aggregate and add nothing of their own.
CAPPED_AGGREGATES = {"household_child_care_subsidies": {"child_care_subsidies"}}

# Members intentionally removed in a year block, keyed by (list, block date).
# Add an entry here when a credit genuinely ends; do not silently drop
# members when copying a block forward.
ALLOWED_REMOVALS = {
    # NY additional Empire State Child Credit was a supplemental payment
    # in 2021 and 2023 only.
    ("gov/states/household/state_ctcs.yaml", "2022-01-01"): {"ny_additional_ctc"},
    ("gov/states/household/state_ctcs.yaml", "2024-01-01"): {"ny_additional_ctc"},
    # Idaho's child tax credit expires after 2025.
    ("gov/states/household/state_ctcs.yaml", "2026-01-01"): {"id_ctc"},
    # From 2023 MN phases its working family credit down jointly with a new
    # child tax credit (Minn. Stat. 290.0661, subd. 4); mn_wfc models only the
    # pre-2023 working family credit formula.
    ("gov/states/household/state_eitcs.yaml", "2023-01-01"): {"mn_wfc"},
    # VT restructured its CDCC into a single vt_cdcc in 2022.
    ("gov/states/household/state_cdccs.yaml", "2022-01-01"): {
        "vt_low_income_cdcc",
        "vt_nonrefundable_cdcc",
    },
}


@pytest.fixture(scope="module")
def variables():
    from policyengine_us.system import system

    return system.variables


def blocks_of(list_path):
    raw = yaml.load((PARAMETERS / list_path).read_text(), Loader=yaml.BaseLoader)
    return sorted(
        (date, members)
        for date, members in raw["values"].items()
        if isinstance(members, list)
    )


def members_of(list_path):
    return {m for _, members in blocks_of(list_path) for m in members}


@pytest.mark.parametrize("list_path", AGGREGATE_LISTS)
def test_members_are_defined_variables(list_path, variables):
    undefined = sorted(members_of(list_path) - set(variables))
    assert not undefined, (
        f"{list_path} references variables that do not exist: {undefined}"
    )


def has_state_gate(variables, member):
    """True when a StateCode (or locality) gate appears in the defined_for chain."""
    gate = variables[member].defined_for
    for _ in range(10):
        if gate is None:
            return False
        if re.fullmatch(r"[A-Z]{2}", str(gate)):
            return True  # StateCode gate found
        if gate in GEOGRAPHIC_GATES:
            return True
        gate = variables[gate].defined_for if gate in variables else None
    return False


def aggregate_members(variables, member):
    """The variables an aggregate member sums, or None if it is not an aggregate.

    `adds` is either a list of variable names or a dotted parameter path
    (e.g. gov.hhs.ccdf.child_care_subsidy_programs). A variable in
    CAPPED_AGGREGATES caps the aggregates it names, so those are its members.
    """
    if member in CAPPED_AGGREGATES:
        return CAPPED_AGGREGATES[member]
    adds = getattr(variables[member], "adds", None)
    if not adds:
        return None
    if isinstance(adds, str):
        list_path = adds.replace(".", "/") + ".yaml"
        if not (PARAMETERS / list_path).exists():
            return None
        return members_of(list_path)
    return set(adds)


def is_state_gated(variables, member, depth=0):
    if has_state_gate(variables, member):
        return True
    # An aggregate whose every summed member is state-gated cannot leak one
    # state's program into other states: each addend is zero outside its gate.
    if depth < 3:
        members = aggregate_members(variables, member)
        if members is not None:
            return all(is_state_gated(variables, m, depth + 1) for m in members)
    return False


@pytest.mark.parametrize("list_path", AGGREGATE_LISTS)
def test_members_are_state_gated(list_path, variables):
    ungated = [
        member
        for member in sorted(members_of(list_path))
        if not is_state_gated(variables, member)
    ]
    assert not ungated, (
        f"{list_path} members without a StateCode gate in their "
        f"defined_for chain (dc_ctc-style leak risk): {ungated}"
    )


# household_benefits and spm_unit_benefits need no state gate, because most
# members are national.
BENEFIT_LISTS = [
    "gov/household/household_benefits.yaml",
    "gov/household/spm_unit_benefits.yaml",
]


@pytest.mark.parametrize("list_path", [*AGGREGATE_LISTS, *BENEFIT_LISTS])
def test_no_silent_removals_between_year_blocks(list_path):
    blocks = blocks_of(list_path)
    for (_, prev), (date, curr) in zip(blocks, blocks[1:]):
        removed = set(prev) - set(curr)
        allowed = ALLOWED_REMOVALS.get((list_path, date), set())
        unexpected = sorted(removed - allowed)
        assert not unexpected, (
            f"{list_path} block {date} drops {unexpected} from the "
            "previous block. These lists are full replacements: copy all "
            "prior members forward, or record an intentional removal in "
            "ALLOWED_REMOVALS in this test."
        )


@pytest.mark.parametrize("list_path", BENEFIT_LISTS)
def test_benefit_list_members_are_defined_variables(list_path, variables):
    undefined = sorted(members_of(list_path) - set(variables))
    assert not undefined, (
        f"{list_path} references variables that do not exist: {undefined}"
    )


@pytest.mark.parametrize("list_path", BENEFIT_LISTS)
def test_benefit_lists_hold_each_member_once(list_path):
    for date, members in blocks_of(list_path):
        repeated = sorted(m for m in set(members) if members.count(m) > 1)
        assert not repeated, f"{list_path} block {date} repeats {repeated}"


# --- Reforms extend the benefit lists rather than copy them ----------------


ADDS_PARAMETER = re.compile(r'^\s+adds\s*=\s*"(gov(?:\.\w+)+)"', re.MULTILINE)


def is_list_parameter(path):
    """True when a dotted path names a parameter whose values are lists."""
    source = PARAMETERS / (path.replace(".", "/") + ".yaml")
    if not source.is_file():
        return False
    raw = yaml.load(source.read_text(), Loader=yaml.BaseLoader)
    values = raw.get("values") if isinstance(raw, dict) else None
    return isinstance(values, dict) and any(
        isinstance(members, list) for members in values.values()
    )


def summed_list(variable, sources):
    """The list parameter a variable sums, or None.

    A total reads a gov.household list of its own name (household_benefits,
    household_health_benefits), or names a list in its adds
    (state_property_tax_refunds adds
    gov.states.household.state_property_tax_refunds).
    """
    own = f"gov.household.{variable}"
    if is_list_parameter(own):
        return own
    for source in sources.get(variable, ()):
        match = ADDS_PARAMETER.search(source.read_text())
        if match and is_list_parameter(match[1]):
            return match[1]
    return None


def benefit_list_totals():
    """{total: the list it sums, or None} for every benefit total.

    The totals are household_benefits, spm_unit_benefits, and each member of
    their lists, at any depth, that sums a list of its own or caps a total in
    CAPPED_AGGREGATES. household_child_care_subsidies sums no list: it caps
    child_care_subsidies, which sums gov.hhs.ccdf.child_care_subsidy_programs.
    A reform that redefines one of these variables, or changes its list, can
    drop a baseline program from the household or SPM totals.
    test_reform_benefit_lists.py derives the same totals from the built model
    and checks that the two agree.
    """
    sources = {}
    for source in (PACKAGE / "variables").rglob("*.py"):
        sources.setdefault(source.stem, []).append(source)
    totals = {}
    pending = ["household_benefits", "spm_unit_benefits"]
    while pending:
        variable = pending.pop()
        if variable in totals:
            continue
        totals[variable] = summed_list(variable, sources)
        members = set(CAPPED_AGGREGATES.get(variable, ()))
        if totals[variable] is not None:
            members |= members_of(totals[variable].replace(".", "/") + ".yaml")
        pending += [
            member
            for member in sorted(members)
            if member in CAPPED_AGGREGATES or summed_list(member, sources)
        ]
    return totals


BENEFIT_LIST_TOTALS = benefit_list_totals()
AGGREGATE_VARIABLES = tuple(sorted(BENEFIT_LIST_TOTALS))
BENEFIT_LIST_PARAMETERS = tuple(
    sorted({path for path in BENEFIT_LIST_TOTALS.values() if path})
)
# What a reform module may not name without a check against the baseline: each
# total, and the last part of each list's path.
GUARDED_NAMES = frozenset(AGGREGATE_VARIABLES) | {
    path.rsplit(".", 1)[1] for path in BENEFIT_LIST_PARAMETERS
}


def test_benefit_totals_include_every_list_that_feeds_household_benefits():
    """The guards below cover a list only while this derivation finds it."""
    expected = {
        "household_benefits": "gov.household.household_benefits",
        "spm_unit_benefits": "gov.household.spm_unit_benefits",
        "household_state_benefits": "gov.household.household_state_benefits",
        "household_local_benefits": "gov.household.household_local_benefits",
        "household_health_benefits": "gov.household.household_health_benefits",
        "household_head_start_benefits": (
            "gov.household.household_head_start_benefits"
        ),
        "state_property_tax_refunds": (
            "gov.states.household.state_property_tax_refunds"
        ),
        "household_child_care_subsidies": None,
        "child_care_subsidies": "gov.hhs.ccdf.child_care_subsidy_programs",
    }
    assert expected.items() <= BENEFIT_LIST_TOTALS.items()


def aggregate_redefinitions(source_text):
    """Names of the benefit aggregates that a module defines a class for.

    Reform modules define their variables inside a create_* function, so the
    walk covers nested classes too.
    """
    return sorted(
        node.name
        for node in ast.walk(ast.parse(source_text))
        if isinstance(node, ast.ClassDef) and node.name in AGGREGATE_VARIABLES
    )


def test_aggregate_redefinitions_finds_a_nested_copy():
    """The scan below is only a guard while it would find a copy."""
    source = (
        "def create_reform():\n"
        "    class spm_unit_benefits(Variable):\n"
        "        pass\n"
        "    class household_benefits(Variable):\n"
        "        pass\n"
        "    class spm_unit_net_income(Variable):\n"
        "        pass\n"
    )
    assert aggregate_redefinitions(source) == [
        "household_benefits",
        "spm_unit_benefits",
    ]


def test_reforms_extend_benefit_lists_rather_than_copy_them():
    copies = [
        f"{source.relative_to(PACKAGE)}::{name}"
        for source in sorted((PACKAGE / "reforms").rglob("*.py"))
        for name in aggregate_redefinitions(source.read_text())
    ]
    assert not copies, (
        f"These reforms redefine a benefit aggregate: {copies}. A copy of the "
        "list falls behind the baseline, and every program it misses drops "
        "out of income for every household the reform applies to (#10226). "
        "Add the reform's own programs to gov.household.household_benefits or "
        "gov.household.spm_unit_benefits with add_to_list_parameter "
        "(policyengine_us/tools/parameters.py) in its modify_parameters."
    )


# A reform can also drop a baseline program by changing a list parameter, or by
# neutralizing a benefit total. test_reform_benefit_lists.py checks each reform
# in its REFORMS: every list parameter in the model must hold, on every day,
# the baseline list followed by the reform's own additions, and every benefit
# total must keep its baseline formula. It builds a full reformed system per
# reform, so it runs in its own CI group; the scan below makes sure no reform
# that names a benefit total or list escapes it.
CHECKED_AGAINST_THE_BASELINE = PACKAGE / "tests/test_reform_benefit_lists.py"

# Strings a variable sets to describe itself, which can name a list without
# reaching it.
DESCRIPTIONS = {"label", "documentation", "reference", "description"}
GUARDED_WORD = re.compile(r"\b(?:%s)\b" % "|".join(sorted(GUARDED_NAMES)))


def benefit_list_references(source_text):
    """The benefit totals and lists a module names.

    Any mention outside comments, docstrings and the strings a variable sets
    to describe itself counts: an attribute, through an alias too
    (``household = parameters.gov.household; household.spm_unit_benefits``),
    a name, a class, an import, and a word in a string
    (``"gov.household.spm_unit_benefits"``,
    ``getattr(household, "household_benefits")``,
    ``neutralize_variable("household_state_benefits")``). A scan cannot tell
    a route that changes a list from one that only reads it, so a reform that
    reads a total by name joins REFORMS too, with no additions of its own. It
    cannot follow a name built at run time, such as an f-string path.
    """
    tree = ast.parse(source_text)
    skipped = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            skipped.add(id(node.value))
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in DESCRIPTIONS
            for target in node.targets
        ):
            skipped.update(id(part) for part in ast.walk(node.value))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            names = [node.attr]
        elif isinstance(node, ast.Name):
            names = [node.id]
        elif isinstance(node, ast.ClassDef):
            names = [node.name]
        elif isinstance(node, ast.alias):
            names = [*node.name.split("."), node.asname]
        elif (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in skipped
        ):
            names = GUARDED_WORD.findall(node.value)
        else:
            continue
        found.update(name for name in names if name in GUARDED_NAMES)
    return sorted(found)


REFERENCE_ROUTES = [
    (
        "parameters.gov.household.spm_unit_benefits.update(value=['snap'])",
        ["spm_unit_benefits"],
    ),
    (
        "household = parameters.gov.household\n"
        "household.household_benefits.update(value=['snap'])",
        ["household_benefits"],
    ),
    (
        "parameters.get_child('gov.household.household_local_benefits')",
        ["household_local_benefits"],
    ),
    (
        "parameters.gov.household.get_child('household_health_benefits')",
        ["household_health_benefits"],
    ),
    (
        "getattr(parameters.gov.household, 'household_head_start_benefits')",
        ["household_head_start_benefits"],
    ),
    (
        "parameters.gov.household.children['household_state_benefits']",
        ["household_state_benefits"],
    ),
    (
        "for name in ('spm_unit_benefits', 'household_benefits'):\n"
        "    getattr(parameters.gov.household, name).update(value=[])",
        ["household_benefits", "spm_unit_benefits"],
    ),
    (
        "self.neutralize_variable('household_state_benefits')",
        ["household_state_benefits"],
    ),
    (
        "parameters.gov.states.household.state_property_tax_refunds.update(value=[])",
        ["state_property_tax_refunds"],
    ),
    (
        "parameters.gov.hhs.ccdf.child_care_subsidy_programs.update(value=[])",
        ["child_care_subsidy_programs"],
    ),
    (
        "class household_child_care_subsidies(Variable):\n    adds = []",
        ["household_child_care_subsidies"],
    ),
    (
        "from policyengine_us.variables.gov.hhs.ccdf.child_care_subsidies "
        "import child_care_subsidies as base",
        ["child_care_subsidies"],
    ),
    (
        "def formula(spm_unit, period, parameters):\n"
        "    return spm_unit('spm_unit_benefits', period)",
        ["spm_unit_benefits"],
    ),
    # What does not reach a list.
    ('"""Mentions gov.household.spm_unit_benefits in a docstring."""', []),
    ("# parameters.gov.household.spm_unit_benefits.update(value=[])", []),
    (
        "class tx_rebate(Variable):\n"
        "    label = 'household_benefits'\n"
        "    documentation = 'Counted in gov.household.spm_unit_benefits.'",
        [],
    ),
    (
        "parameters.gov.household.household_benefits_cap.update(value=1)\n"
        "spm_unit('cbo_household_benefits', period)",
        [],
    ),
]


@pytest.mark.parametrize("source, expected", REFERENCE_ROUTES)
def test_benefit_list_references_finds_each_route(source, expected):
    """The scan below is only a guard while it finds each route."""
    assert benefit_list_references(source) == expected


def reforms_checked_against_the_baseline():
    """Source files of the reforms in test_reform_benefit_lists.REFORMS.

    Read from that file's syntax tree: importing it would build the full
    model at collection time.
    """
    tree = ast.parse(CHECKED_AGAINST_THE_BASELINE.read_text())
    imported = {
        alias.asname or alias.name: node.module
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and (node.module or "").startswith("policyengine_us.reforms.")
        for alias in node.names
    }
    registries = [
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "REFORMS" for t in node.targets)
    ]
    assert len(registries) == 1 and isinstance(registries[0], ast.Dict), (
        f"{CHECKED_AGAINST_THE_BASELINE.name} no longer defines REFORMS as a dict"
    )
    sources = set()
    for value in registries[0].values:
        reform = value.elts[0] if isinstance(value, ast.Tuple) else value
        assert isinstance(reform, ast.Name) and reform.id in imported, (
            f"REFORMS holds {ast.dump(reform)}, not a reform imported from "
            "policyengine_us.reforms"
        )
        module = imported[reform.id].split(".")[1:]
        sources.add("/".join(module) + ".py")
    return sources


def test_reforms_that_reach_a_benefit_list_are_checked_against_the_baseline():
    checked = reforms_checked_against_the_baseline()
    assert len(checked) >= 4, checked
    reaching = {
        str(source.relative_to(PACKAGE)): benefit_list_references(source.read_text())
        for source in sorted((PACKAGE / "reforms").rglob("*.py"))
    }
    unchecked = {
        source: lists
        for source, lists in reaching.items()
        if lists and source not in checked
    }
    assert not unchecked, (
        f"These reforms name a benefit total or list without a check that "
        f"they keep every baseline program: {unchecked}. Add each to REFORMS "
        "in test_reform_benefit_lists.py, which fails when a reform changes a "
        "list parameter beyond its own additions or neutralizes a benefit "
        "total, and extend the lists only with add_to_list_parameter "
        "(policyengine_us/tools/parameters.py)."
    )
    assert not checked - set(reaching), (
        f"REFORMS names reforms with no source file: {checked - set(reaching)}"
    )


# --- Household tax totals -------------------------------------------------

HOUSEHOLD_TAX_TOTALS = {
    "household_tax_before_refundable_credits",
    "household_state_tax_before_refundable_credits",
    "state_income_tax_before_refundable_credits",
    "state_use_tax",
    "local_income_tax_before_refundable_credits",
    "local_occupational_tax",
    "household_refundable_tax_credits",
    "income_tax_refundable_credits_in_force",
    "federal_income_tax_in_force",
    "household_refundable_state_tax_credits",
    "household_refundable_local_tax_credits",
    "household_tax",
    "household_net_income",
}


def test_no_reform_redefines_a_household_tax_total():
    """Change a component or the baseline formula instead of copying a total.

    A copy keeps the components it was written with, so it misses any that
    the baseline total gains later.
    """
    redefinitions = []
    for source in sorted((PACKAGE / "reforms").rglob("*.py")):
        tree = ast.parse(source.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in HOUSEHOLD_TAX_TOTALS:
                redefinitions.append(f"{source.relative_to(PACKAGE)}::{node.name}")
    assert not redefinitions, (
        "Reforms redefine household tax totals, which then drift from the "
        f"baseline: {redefinitions}"
    )


# Components that the abolish parameters zero in their own formulas. The
# household totals rely on those checks, so a reform that replaces one of
# these variables must keep reading the parameter.
ABOLITION_CHECKS = {
    "income_tax": "abolish_federal_income_tax",
    "income_tax_before_refundable_credits": "abolish_federal_income_tax",
    "income_tax_chapter_1": "abolish_federal_income_tax",
    "employee_payroll_tax": "abolish_payroll_tax",
}


def test_reforms_replacing_an_abolished_tax_keep_the_abolition_check():
    """A replacement without the check would charge the tax again.

    Before the abolish parameters relied on the baseline formulas alone, the
    structural reforms dropped the abolished tax from the household total by
    name. Now only the check inside each formula drops it.
    """
    missing = []
    for source in sorted((PACKAGE / "reforms").rglob("*.py")):
        tree = ast.parse(source.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in ABOLITION_CHECKS:
                reads_parameter = any(
                    isinstance(child, ast.Attribute)
                    and child.attr == ABOLITION_CHECKS[node.name]
                    for child in ast.walk(node)
                )
                if not reads_parameter:
                    missing.append(f"{source.relative_to(PACKAGE)}::{node.name}")
    assert not missing, (
        "Reforms replace a tax the abolish parameters zero without reading "
        f"the parameter: {missing}"
    )
