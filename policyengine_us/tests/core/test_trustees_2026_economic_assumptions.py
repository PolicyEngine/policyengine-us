"""The 2026 Trustees economic assumptions move Social Security's wage and
price paths, and everything built on them, for long-range scoring only.

Expected values come from arithmetic written here on the Trustees' table,
from published values in the default tree, or from pins computed separately
from the Trustees' workbook. No expectation calls the extension functions the
module reuses.

Cost: the module builds one reformed system and copies the default tree once,
both cached. It builds one more system, the assumption plus a cap-only policy,
and keeps only the values its tests compare. The two composition tests, last,
free them and each build one more system, keeping only the values they
compare.
"""

import hashlib
import math
from contextlib import contextmanager
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import pytest
import yaml
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import Parameter, ParameterNode
from policyengine_core.parameters.operations.get_parameter import get_parameter
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.reforms.ssa import (
    TRUSTEES_2026_ADJUSTED_CPI as ACPI,
    TRUSTEES_2026_AVERAGE_WAGE_INDEX as AWI,
    TRUSTEES_2026_ECONOMIC_ASSUMPTION,
    apply_trustees_2026_economic_assumptions,
    apply_trustees_2026_nawi_projection,
    apply_trustees_2026_price_projection,
    create_trustees_2026_economic_assumptions_reform,
    trustees_2026_economic_assumptions_reform,
    trustees_core_thresholds_reform,
)
from policyengine_us.reforms.ssa.trustees_2025 import (
    TRUSTEES_2025_SOI_INCOME_UPRATING_PARAMETERS,
)
from policyengine_us.reforms.ssa.trustees_2026 import (
    apply_trustees_2026_path_readers,
    trustees_2026_path_readers,
)
from policyengine_us.reforms.ssa.trustees_core_thresholds import (
    _iter_updatable_parameters,
)
from policyengine_us.system import system
from policyengine_us.tools.social_security_benefit_levers import cola_events

NAWI = "gov.ssa.nawi"
UPRATING = "gov.ssa.uprating"
CAP = "gov.irs.payroll.social_security.cap"
OWNERS_DRAW_CAP = "gov.contrib.ssa.owners_draw.current_law_cap"
SOCIAL_SECURITY = "gov.ssa.social_security"
WAGE_BASE = f"{SOCIAL_SECURITY}.wage_base"
QC_THRESHOLD = f"{SOCIAL_SECURITY}.quarters_of_coverage_threshold"
EXEMPT_UNDER_FRA = f"{SOCIAL_SECURITY}.earnings_test.exempt_amount_under_fra"
EXEMPT_YEAR_OF_FRA = f"{SOCIAL_SECURITY}.earnings_test.exempt_amount_year_of_fra"
BEND_POINT_1 = f"{SOCIAL_SECURITY}.pia.formula_factors[1].threshold"
BEND_POINT_2 = f"{SOCIAL_SECURITY}.pia.formula_factors[2].threshold"
SGA_NON_BLIND = "gov.ssa.sga.non_blind"
SGA_BLIND = "gov.ssa.sga.blind"
WAGE_INDEXED = (
    WAGE_BASE,
    QC_THRESHOLD,
    EXEMPT_UNDER_FRA,
    EXEMPT_YEAR_OF_FRA,
    BEND_POINT_1,
    BEND_POINT_2,
    SGA_NON_BLIND,
    SGA_BLIND,
)
SOI_TOTALS = tuple(
    f"calibration.gov.irs.soi.{name}"
    for name in TRUSTEES_2025_SOI_INCOME_UPRATING_PARAMETERS
)
# Parameters whose uprating metadata names each path (the cap names NAWI too,
# but the cap extension sets it), as a walk of the tree found them.
UPRATING_READERS = (
    "gov.ssa.ssi.amount.couple",
    "gov.ssa.ssi.amount.individual",
    "gov.ssa.ssi.income.exclusions.blind_or_disabled_working_student.amount",
    "gov.ssa.ssi.income.exclusions.blind_or_disabled_working_student.cap",
    "gov.states.ak.dpa.ssp.income_eligibility_standard.couple",
    "gov.states.ak.dpa.ssp.income_eligibility_standard.individual",
    "gov.states.ia.hhs.ssa.rcf_personal_needs",
    "gov.states.md.tax.income.agi.subtractions.pension.max_amount",
    "gov.states.nc.ncdhhs.sa.rate.basic",
    "gov.states.nc.ncdhhs.sa.rate.enhanced",
    "gov.states.ok.dhs.ssp.child_allocation",
    "gov.states.ok.dhs.ssp.ineligible_spouse_standard",
    "gov.states.sd.dss.ssp.assisted_living_daily_rate",
)
NAWI_READERS = (
    "gov.irs.income.exemption.overtime.hce_salary_threshold",
    "gov.irs.income.exemption.overtime.salary_basis_threshold",
)
TOUCHED = (
    NAWI,
    UPRATING,
    CAP,
    OWNERS_DRAW_CAP,
    *WAGE_INDEXED,
    *SOI_TOTALS,
    *UPRATING_READERS,
    *NAWI_READERS,
)

PUBLISHED_NAWI_2025 = 72_800.33
LAST_ACTUAL_UPRATING_2027 = 328.746  # 2026 third-quarter CPI-W
LAST_TABLE_YEAR = 2100

# Pins from separate arithmetic on the Trustees' workbook:
# (path, year, pin, half a unit in the pin's last place).
PINS = (
    (NAWI, 2026, 76_056.64, 0.005),
    (NAWI, 2034, 106_176.27, 0.005),
    (NAWI, 2098, 1_004_086.40, 0.005),
    (NAWI, 2100, 1_076_751.82, 0.005),
    (UPRATING, 2028, 336.833, 0.0005),
    (UPRATING, 2050, 567.58, 0.005),
    (UPRATING, 2100, 1_857.875, 0.0005),
    (CAP, 2028, 201_000, 0),
    (CAP, 2050, 462_900, 0),
    (CAP, 2100, 2_652_900, 0),
)

# sha256 of "year,AWI,adjusted CPI" lines, to two decimals, for 2025 to 2100,
# from an extraction of Table VI.G1 (workbook sha256 38d8c5fe...ba361) checked
# against a second extraction and Table V.B1.
TABLE_FINGERPRINT = "513cf8fa5aab105649fba4b5dff0a7a9b65005121fcb4636f624b5c5ec94b7a9"


def _value(tree, path, year):
    return get_parameter(tree, path)(f"{year}-01-01")


def _entries(tree, path, through=None):
    return [
        (entry.instant_str, entry.value)
        for entry in get_parameter(tree, path).values_list
        if through is None or entry.instant_str <= through
    ]


def _snapshot(tree):
    return {path: _entries(tree, path) for path in TOUCHED}


# Taken before this module builds anything from the default tree.
DEFAULT_BEFORE = _snapshot(system.parameters)


@pytest.fixture(scope="module", autouse=True)
def _release_cached_systems():
    """Free the systems this module builds before later modules run."""
    yield
    for cached in (_reformed_system, _applied_once, _end_to_end, _cap_policy_run):
        cached.cache_clear()


@lru_cache(maxsize=1)
def _reformed_system():
    # System init applies a reform set twice.
    return CountryTaxBenefitSystem(reform=trustees_2026_economic_assumptions_reform)


def _reformed():
    return _reformed_system().parameters


@lru_cache(maxsize=1)
def _applied_once():
    tree = system.parameters.clone()
    apply_trustees_2026_economic_assumptions(tree)
    return tree


def _tr_nawi(year):
    """NAWI on the Trustees' path, from the table's level ratio to 2025."""
    if year <= 2025:
        return _value(system.parameters, NAWI, year)
    year = min(year, LAST_TABLE_YEAR)
    return PUBLISHED_NAWI_2025 * AWI[year] / AWI[2025]


def _tr_uprating(year):
    """The COLA index on the Trustees' path: CPI of the year before."""
    if year <= 2027:
        return _value(system.parameters, UPRATING, year)
    year = min(year, LAST_TABLE_YEAR)
    return LAST_ACTUAL_UPRATING_2027 * ACPI[year - 1] / ACPI[2026]


def _round_half_up(amount, increment):
    """The nearest multiple of ``increment``; a half rounds up."""
    steps = (Decimal(amount) / Decimal(increment)).quantize(
        Decimal(1), rounding=ROUND_HALF_UP
    )
    return float(steps * Decimal(increment))


# Each automatic determination for year Y scales a base amount by NAWI(Y - 2)
# over a base year's NAWI: (amount, base NAWI year, rounding increment,
# months, never below the year before). 42 U.S.C. 430(b) sets the cap's.
STATUTORY = {
    CAP: (60_600, 1992, 300, 1, True),
    QC_THRESHOLD: (250, 1976, 10, 1, True),
    EXEMPT_UNDER_FRA: (670, 1992, 10, 12, True),
    EXEMPT_YEAR_OF_FRA: (2_500, 2000, 10, 12, True),
    BEND_POINT_1: (180, 1977, 1, 1, False),
    BEND_POINT_2: (1_085, 1977, 1, 1, False),
    SGA_NON_BLIND: (700, 1998, 10, 1, True),
    SGA_BLIND: (930, 1992, 10, 1, True),
}


@lru_cache(maxsize=None)
def _statutory_path(path):
    """Each year's amount on the Trustees' NAWI, from 2027's published one."""
    amount, base_year, increment, months, floored = STATUTORY[path]
    base_nawi = _value(system.parameters, NAWI, base_year)
    values = {2027: _value(system.parameters, path, 2027)}
    for year in range(2028, LAST_TABLE_YEAR + 1):
        value = months * _round_half_up(
            amount * _tr_nawi(year - 2) / base_nawi, increment
        )
        values[year] = max(values[year - 1], value) if floored else value
    return values


def test_series_match_the_extracted_table():
    assert sorted(AWI) == sorted(ACPI) == list(range(2025, LAST_TABLE_YEAR + 1))
    assert ACPI[2026] == 100
    lines = "\n".join(
        f"{year},{AWI[year]:.2f},{ACPI[year]:.2f}" for year in range(2025, 2101)
    )
    assert hashlib.sha256(lines.encode()).hexdigest() == TABLE_FINGERPRINT


def test_assumption_is_explicit_and_off_by_default():
    assert TRUSTEES_2026_ECONOMIC_ASSUMPTION["name"] == "trustees-2026-economic-v1"
    assert TRUSTEES_2026_ECONOMIC_ASSUMPTION["not_default_current_law"] is True
    assert TRUSTEES_2026_ECONOMIC_ASSUMPTION["start_year"] == 2026
    assert TRUSTEES_2026_ECONOMIC_ASSUMPTION["end_year"] == 2100


@pytest.mark.parametrize("end_year", [2027, 2101])
def test_end_year_outside_the_table_is_refused(end_year):
    with pytest.raises(ValueError, match="end_year"):
        create_trustees_2026_economic_assumptions_reform(end_year=end_year)
    with pytest.raises(ValueError, match="end_year"):
        apply_trustees_2026_economic_assumptions(None, end_year=end_year)


@pytest.mark.parametrize("path, year, pin, tolerance", PINS)
def test_pins(path, year, pin, tolerance):
    value = _value(_reformed(), path, year)
    if tolerance:
        assert abs(value - pin) <= tolerance
    else:
        assert value == pin


def test_chain_identities_hold_for_every_year():
    tree = _reformed()
    for year in range(2026, LAST_TABLE_YEAR + 1):
        assert _value(tree, NAWI, year) / _value(tree, NAWI, year - 1) == (
            pytest.approx(AWI[year] / AWI[year - 1], rel=1e-12)
        ), year
        assert _value(tree, NAWI, year) == pytest.approx(_tr_nawi(year), rel=1e-12)
    for year in range(2028, LAST_TABLE_YEAR + 1):
        assert _value(tree, UPRATING, year) / _value(tree, UPRATING, year - 1) == (
            pytest.approx(ACPI[year - 1] / ACPI[year - 2], rel=1e-12)
        ), year
        assert _value(tree, UPRATING, year) == pytest.approx(
            _tr_uprating(year), rel=1e-12
        )


@pytest.mark.parametrize("path", STATUTORY)
def test_wage_indexed_amounts_follow_the_statutory_formula(path):
    tree = _reformed()
    expected = _statutory_path(path)
    for year in range(2028, LAST_TABLE_YEAR + 1):
        assert _value(tree, path, year) == expected[year], (path, year)
    for year in (2028, 2036, 2037, 2060, 2100):
        assert _value(tree, path, year) != _value(system.parameters, path, year)


def test_wage_base_equals_the_cap():
    tree = _reformed()
    for year in range(2027, LAST_TABLE_YEAR + 1):
        assert _value(tree, WAGE_BASE, year) == _statutory_path(CAP)[year]
    for year in (2028, 2036, 2037, 2060, 2100):
        assert _value(tree, WAGE_BASE, year) != _value(
            system.parameters, WAGE_BASE, year
        )


def test_owners_draw_current_law_cap_follows_the_assumption():
    tree = _reformed()
    for year in range(2028, LAST_TABLE_YEAR + 1):
        assert _value(tree, OWNERS_DRAW_CAP, year) == _value(tree, CAP, year), year
    assert _entries(tree, OWNERS_DRAW_CAP, "2027-12-31") == _entries(
        system.parameters, CAP, "2027-12-31"
    )


def test_owners_draw_current_law_cap_pins():
    assert _value(system.parameters, OWNERS_DRAW_CAP, 2060) == 558_600
    assert _value(_reformed(), OWNERS_DRAW_CAP, 2060) == 654_900


def test_owners_draw_current_law_cap_holds_after_one_cap_policy_from_2028():
    """One pass: after the assumption, a policy sets the payroll cap from
    2028, and the assumption's copy holds.

    Reuse the cached default-tree copy and restore its cap after the check.
    """
    tree = _applied_once()
    expected_copy = _entries(tree, OWNERS_DRAW_CAP)
    cap = get_parameter(tree, CAP)
    original_values = cap.values_list
    try:
        cap.update(start="2028-01-01", value=10_000_000)
        for year in range(2028, LAST_TABLE_YEAR + 1):
            assert _value(tree, CAP, year) == 10_000_000, year
            assert _value(tree, OWNERS_DRAW_CAP, year) == _statutory_path(CAP)[year], (
                year
            )
        assert _entries(tree, OWNERS_DRAW_CAP) == expected_copy
    finally:
        cap.values_list = original_values
        cap.parent.clear_parent_cache()


@contextmanager
def _on_default_values(tree):
    """Put each touched parameter of the cached copy on the default tree's
    values, then give the copy its own values back.

    Core's ``update`` replaces a parameter's value list and never edits the
    entries in it, so the copy can share the default tree's entries meanwhile.
    """
    parameters = {path: get_parameter(tree, path) for path in TOUCHED}
    before = _snapshot(tree)
    own = {path: parameter.values_list for path, parameter in parameters.items()}

    def put(values_by_path):
        for path, parameter in parameters.items():
            parameter.values_list = list(values_by_path[path])
            parameter.parent.clear_parent_cache()

    put({path: get_parameter(system.parameters, path).values_list for path in TOUCHED})
    try:
        yield
    finally:
        put(own)
    assert _snapshot(tree) == before
    _assert_default_tree_untouched()


CAP_POLICIES = {"cap_removed": math.inf, "cap_of_10_million": 10_000_000}


@pytest.mark.parametrize("order", ["assumption_first", "policy_first"])
@pytest.mark.parametrize("policy_cap", CAP_POLICIES.values(), ids=CAP_POLICIES)
def test_owners_draw_current_law_cap_survives_both_passes_of_a_2027_cap_policy(
    policy_cap, order
):
    """A built system applies its reform set twice. Replay both passes with a
    policy that sets the payroll cap from 2027, in either tuple order: the
    policy's 2027 cap must not become the copy's no-decrease floor."""

    def policy(parameters):
        get_parameter(parameters, CAP).update(start="2027-01-01", value=policy_cap)

    reform_set = (apply_trustees_2026_economic_assumptions, policy)
    if order == "policy_first":
        reform_set = reform_set[::-1]
    tree = _applied_once()
    with _on_default_values(tree):
        for apply in reform_set * 2:
            apply(tree)
        assert _value(tree, OWNERS_DRAW_CAP, 2060) == 654_900
        for year in range(2028, LAST_TABLE_YEAR + 1):
            assert _value(tree, OWNERS_DRAW_CAP, year) == _statutory_path(CAP)[year], (
                year
            )
        assert _entries(tree, OWNERS_DRAW_CAP, "2027-12-31") == _entries(
            system.parameters, CAP, "2027-12-31"
        )
        for year in range(2027, LAST_TABLE_YEAR + 1):
            assert _value(tree, CAP, year) == policy_cap, year


@pytest.mark.parametrize("order", ["assumption_first", "policy_first"])
@pytest.mark.parametrize("policy_cap", CAP_POLICIES.values(), ids=CAP_POLICIES)
def test_wage_base_survives_both_passes_of_a_2027_cap_policy(policy_cap, order):
    """A policy that sets only the payroll cap from 2027 leaves the benefit
    wage base on the assumption's path after both passes, in either order."""

    def policy(parameters):
        get_parameter(parameters, CAP).update(start="2027-01-01", value=policy_cap)

    reform_set = (apply_trustees_2026_economic_assumptions, policy)
    if order == "policy_first":
        reform_set = reform_set[::-1]
    tree = _applied_once()
    with _on_default_values(tree):
        for apply in reform_set * 2:
            apply(tree)
        for year in range(2027, LAST_TABLE_YEAR + 1):
            assert _value(tree, CAP, year) == policy_cap, year
            assert _value(tree, WAGE_BASE, year) == _statutory_path(CAP)[year], year


COPY_POLICY_CAP = 10_000_000


@pytest.mark.parametrize("order", ["assumption_first", "policy_first"])
def test_wage_base_survives_both_passes_of_a_2027_owners_draw_copy_policy(order):
    """A policy that sets only the owners' draw copy from 2027 leaves the
    benefit wage base equal to the assumption baseline's, entry for entry,
    after both passes, in either order."""

    def policy(parameters):
        get_parameter(parameters, OWNERS_DRAW_CAP).update(
            start="2027-01-01", value=COPY_POLICY_CAP
        )

    reform_set = (apply_trustees_2026_economic_assumptions, policy)
    if order == "policy_first":
        reform_set = reform_set[::-1]
    baseline = _entries(_reformed(), WAGE_BASE)
    tree = _applied_once()
    with _on_default_values(tree):
        for apply in reform_set * 2:
            apply(tree)
        assert _entries(tree, WAGE_BASE) == baseline
        for year in range(2027, LAST_TABLE_YEAR + 1):
            assert _value(tree, OWNERS_DRAW_CAP, year) == COPY_POLICY_CAP, year


def test_a_policy_after_the_assumption_keeps_the_wage_base_it_sets():
    """A policy that means to credit the newly taxed earnings sets the wage
    base itself. After the assumption in the tuple, it applies last in both
    passes, so its wage base stands."""

    def policy(parameters):
        for path in (CAP, WAGE_BASE):
            get_parameter(parameters, path).update(start="2027-01-01", value=math.inf)

    tree = _applied_once()
    with _on_default_values(tree):
        for apply in (apply_trustees_2026_economic_assumptions, policy) * 2:
            apply(tree)
        for year in range(2027, LAST_TABLE_YEAR + 1):
            assert _value(tree, WAGE_BASE, year) == math.inf, year
        assert _entries(tree, WAGE_BASE, "2026-12-31") == _entries(
            system.parameters, WAGE_BASE, "2026-12-31"
        )


def _cap_policy(value, start_year=2027):
    def modify_parameters(parameters):
        get_parameter(parameters, CAP).update(start=f"{start_year}-01-01", value=value)
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def _leaves(tree):
    return {
        parameter.name: _entries(tree, parameter.name)
        for parameter in tree.get_descendants()
        if isinstance(parameter, Parameter)
    }


HOUSEHOLD_YEAR = 2027
HOUSEHOLD_WAGES = 500_000


@lru_cache(maxsize=1)
def _cap_policy_run():
    """Build the assumption plus a policy that removes the payroll cap from
    2027, and keep only every parameter's values and one worker's covered
    earnings, so the system itself is freed."""
    built = CountryTaxBenefitSystem(
        reform=(trustees_2026_economic_assumptions_reform, _cap_policy(math.inf))
    )
    situation = {
        "people": {
            "worker": {
                "age": {HOUSEHOLD_YEAR: 40},
                "employment_income": {HOUSEHOLD_YEAR: HOUSEHOLD_WAGES},
            }
        }
    }
    simulation = Simulation(situation=situation, tax_benefit_system=built)
    covered = simulation.calculate("ss_covered_earnings_this_year", HOUSEHOLD_YEAR)
    return _leaves(built.parameters), float(covered[0])


def test_a_cap_only_policy_moves_no_other_parameter():
    """In a built system, a policy that changes only the payroll cap leaves
    every other parameter equal to the assumption baseline's, entry for
    entry. The replayed passes stand for this build."""
    with_policy, _ = _cap_policy_run()
    baseline = _leaves(_reformed())
    assert with_policy.keys() == baseline.keys()
    differ = sorted(name for name in baseline if with_policy[name] != baseline[name])
    assert differ == [CAP]
    for year in range(2027, LAST_TABLE_YEAR + 1):
        assert _value(_reformed(), WAGE_BASE, year) == _statutory_path(CAP)[year]


def test_covered_earnings_stop_at_the_wage_base_under_a_cap_only_policy():
    """A worker earning $500,000 in 2027, with the payroll cap removed from
    2027 under the assumption, is credited only up to the assumption's 2027
    wage base."""
    _, covered = _cap_policy_run()
    assert covered == _statutory_path(CAP)[HOUSEHOLD_YEAR] == 192_300


@pytest.mark.parametrize("end_year", [2028, 2030, 2036])
def test_a_short_end_year_keeps_the_cbo_income_totals(end_year):
    """The SOI helper holds each total at its end_year value from end_year
    on, so the assumption skips it for an end_year of 2036 or earlier."""
    tree = _applied_once()
    with _on_default_values(tree):
        apply_trustees_2026_economic_assumptions(tree, end_year=end_year)
        for path in SOI_TOTALS:
            assert _entries(tree, path, "2036-12-31") == _entries(
                system.parameters, path, "2036-12-31"
            ), path
            assert _value(tree, path, 2040) == _value(system.parameters, path, 2040), (
                path
            )


def test_the_tree_has_the_expected_readers():
    """A new reader of either path needs a look before it joins the reach."""

    def reads(parameter, path):
        uprating = parameter.metadata.get("uprating")
        if isinstance(uprating, dict):
            uprating = uprating.get("parameter")
        return uprating == path

    parameters = [
        parameter
        for parameter in system.parameters.get_descendants()
        if isinstance(parameter, Parameter)
    ]
    for path, readers in ((UPRATING, UPRATING_READERS), (NAWI, NAWI_READERS)):
        found = {p.name for p in parameters if reads(p, path)} - {CAP}
        assert found == set(readers)
    assert {
        path: sorted(p.name for p in found)
        for path, found in trustees_2026_path_readers(system.parameters).items()
    } == {NAWI: sorted(NAWI_READERS), UPRATING: sorted(UPRATING_READERS)}


@lru_cache(maxsize=None)
def _stated(path):
    """A reader's last value in its YAML file, its date and its uprating."""
    parameter = get_parameter(system.parameters, path)
    data = yaml.safe_load(Path(parameter.file_path).read_text())
    values = {
        str(date): value["value"] if isinstance(value, dict) else value
        for date, value in data["values"].items()
    }
    last = max(values)
    return last, values[last], data["metadata"]["uprating"]


def _rounding(uprating):
    return uprating.get("rounding") if isinstance(uprating, dict) else None


def _exact(value):
    return Fraction(repr(value))


def _tr_nawi_exact(year):
    year = min(year, LAST_TABLE_YEAR)
    return _exact(PUBLISHED_NAWI_2025) * _exact(AWI[year]) / _exact(AWI[2025])


def _tr_uprating_exact(year):
    year = min(year, LAST_TABLE_YEAR)
    return (
        _exact(LAST_ACTUAL_UPRATING_2027) * _exact(ACPI[year - 1]) / _exact(ACPI[2026])
    )


def _uprated(path, driver, exact_path, year):
    """Core's uprating: the last stated value times the driver's ratio.

    Returns each value core could round to. The Trustees' CPI has two decimals
    and 2026 = 100, so an amount stated for 2027 can land exactly halfway
    between rounding steps ($2,500 x 136.20 / 100 = $3,405 for the working
    student exclusion in 2039). Core rounds the float it computes there, so
    either neighbor can come out.
    """
    last, value, uprating = _stated(path)
    start = _exact(get_parameter(system.parameters, driver)(last))
    exact = _exact(value) * exact_path(year) / start
    rounding = _rounding(uprating)
    if not rounding:
        return [float(exact)]
    assert rounding["type"] == "nearest"
    interval = _exact(rounding["interval"])
    steps = exact / interval
    low = math.floor(steps)
    if steps - low == Fraction(1, 2):
        return [float(low * interval), float((low + 1) * interval)]
    return [float(round(steps) * interval)]


def _is_one_of(value, candidates):
    return any(value == pytest.approx(c, rel=1e-12) for c in candidates)


READER_CASES = [
    *[(path, UPRATING, _tr_uprating_exact, 2027) for path in UPRATING_READERS],
    *[(path, NAWI, _tr_nawi_exact, 2025) for path in NAWI_READERS],
]


@pytest.mark.parametrize("path, driver, tr_path, last_unchanged", READER_CASES)
def test_readers_follow_the_new_path(path, driver, tr_path, last_unchanged):
    last, _, _ = _stated(path)
    assert last <= f"{last_unchanged}-12-31"
    tree = _reformed()

    def default_path(year):
        return _exact(_value(system.parameters, driver, year))

    for year in range(last_unchanged + 1, LAST_TABLE_YEAR + 1):
        # The formula reproduces the default tree from the default path...
        default = _uprated(path, driver, default_path, year)
        assert _is_one_of(_value(system.parameters, path, year), default), year
        # ...and the reformed tree from the Trustees' path.
        expected = _uprated(path, driver, tr_path, year)
        assert _is_one_of(_value(tree, path, year), expected), year
    rounded = _rounding(_stated(path)[2]) is not None
    for year in (last_unchanged + 1, 2028, 2060):
        if year == 2060 or not rounded:
            assert _value(tree, path, year) != _value(system.parameters, path, year)


PUBLISHED_CASES = [
    (NAWI, 2025),
    (UPRATING, 2027),
    (CAP, 2027),
    (OWNERS_DRAW_CAP, 2027),
    *[(path, 2027) for path in WAGE_INDEXED],
    *[(path, 2036) for path in SOI_TOTALS],
    *[(path, 2027) for path in UPRATING_READERS],
    *[(path, 2025) for path in NAWI_READERS],
]


@pytest.mark.parametrize("path, last_unchanged", PUBLISHED_CASES)
def test_published_years_hold(path, last_unchanged):
    through = f"{last_unchanged}-12-31"
    assert _entries(_reformed(), path, through) == _entries(
        system.parameters, path, through
    )


def _assert_default_tree_untouched():
    assert _snapshot(system.parameters) == DEFAULT_BEFORE
    assert abs(_value(system.parameters, NAWI, 2036) - 104_988.75) <= 0.005
    assert _value(system.parameters, CAP, 2100) == 1_995_300
    assert _value(system.parameters, UPRATING, 2036) == 403.287


def test_reform_leaves_the_default_tree_alone():
    _reformed()
    _assert_default_tree_untouched()


def test_function_leaves_the_default_tree_alone():
    _applied_once()
    _assert_default_tree_untouched()


def test_once_on_a_copy_matches_twice_in_a_built_system():
    """Applying the function once gives every value the built system holds
    after applying the reform twice."""
    assert _snapshot(_applied_once()) == _snapshot(_reformed())


END_TO_END_YEAR = 2060
AIME = 30_000
VETERANS_BENEFITS_2026 = 30_000


def _people_situation():
    people = {
        "earner": {
            "age": {END_TO_END_YEAR: 45},
            "employment_income": {END_TO_END_YEAR: 5_000_000},
        },
        # Born in 1998, first eligible in 2060. Supplying the AIME skips the
        # earnings-history lookback, which the bend points don't touch.
        "retiree": {
            "age": {END_TO_END_YEAR: 62},
            "ss_aime": {END_TO_END_YEAR: AIME},
        },
        "veteran": {
            "age": {2026: 50, END_TO_END_YEAR: 84},
            "veterans_benefits": {2026: VETERANS_BENEFITS_2026},
        },
    }
    return {
        "people": people,
        "tax_units": {f"{name}_unit": {"members": [name]} for name in people},
        "households": {
            f"{name}_household": {
                "members": [name],
                "state_code": {END_TO_END_YEAR: "TX"},
            }
            for name in people
        },
    }


@lru_cache(maxsize=None)
def _end_to_end(reformed):
    tax_benefit_system = _reformed_system() if reformed else system
    simulation = Simulation(
        situation=_people_situation(), tax_benefit_system=tax_benefit_system
    )
    return {
        name: tuple(float(x) for x in simulation.calculate(name, END_TO_END_YEAR))
        for name in (
            "taxable_earnings_for_social_security",
            "ss_pia",
            "veterans_benefits",
        )
    }


def test_taxable_earnings_stop_at_the_new_cap():
    reformed = _end_to_end(True)["taxable_earnings_for_social_security"][0]
    default = _end_to_end(False)["taxable_earnings_for_social_security"][0]
    assert reformed == _statutory_path(CAP)[END_TO_END_YEAR] == 654_900
    assert default == _value(system.parameters, CAP, END_TO_END_YEAR) == 558_600


def test_pia_uses_the_new_bend_points():
    bend_1 = _statutory_path(BEND_POINT_1)[END_TO_END_YEAR]
    bend_2 = _statutory_path(BEND_POINT_2)[END_TO_END_YEAR]
    assert bend_2 < AIME
    pia = 0.90 * bend_1 + 0.32 * (bend_2 - bend_1) + 0.15 * (AIME - bend_2)
    expected = math.floor(pia * 10) / 10
    # Simulations return float32, good to a cent at this size.
    assert _end_to_end(True)["ss_pia"][1] == pytest.approx(expected, abs=0.01)
    assert _end_to_end(False)["ss_pia"][1] != pytest.approx(expected, abs=1)


def test_veterans_benefits_uprate_on_the_path_in_force():
    """Core uprates an input from the system's own index when a later year
    asks for it, so a household's veterans' benefits follow the reform."""

    def default_uprating(year):
        return _value(system.parameters, UPRATING, year)

    for reformed, index in ((True, _tr_uprating), (False, default_uprating)):
        expected = VETERANS_BENEFITS_2026 * index(END_TO_END_YEAR) / index(2026)
        value = _end_to_end(reformed)["veterans_benefits"][2]
        assert value == pytest.approx(expected, rel=1e-6)
    assert _end_to_end(True)["veterans_benefits"][2] > (
        _end_to_end(False)["veterans_benefits"][2] * 1.01
    )


COLA_THROUGH = 2040


def _cola_rate(index, year):
    change = Decimal(repr(index(year))) / Decimal(repr(index(year - 1)))
    return float((change - 1).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def test_cola_lever_reads_the_new_path():
    # Each year the lever reads builds the whole tree at that instant, so a
    # short horizon keeps this cheap; the paths part from the 2029 COLA.
    reformed = {
        event["payment_year"]: event["rate"]
        for event in cola_events(_reformed(), COLA_THROUGH)
        if event["source"] == "gov.ssa.uprating"
    }
    assert sorted(reformed) == list(range(2027, COLA_THROUGH + 1))

    def default_uprating(year):
        return _value(system.parameters, UPRATING, year)

    for year, rate in reformed.items():
        assert rate == _cola_rate(_tr_uprating, year), year
    assert reformed[2027] == _cola_rate(default_uprating, 2027)
    assert reformed[2029] != _cola_rate(default_uprating, 2029)


def _small_tree(**children):
    return ParameterNode("", data=children, file_path="small_tree.yaml")


def _series(path, last_year):
    return {
        f"{year}-01-01": _value(system.parameters, path, year)
        for year in range(1951, last_year + 1)
        if _value(system.parameters, path, year) is not None
    }


def test_paths_hold_their_end_year_value():
    tree = _small_tree(
        gov={
            "ssa": {
                "nawi": {"values": _series(NAWI, 2034)},
                "uprating": {"values": _series(UPRATING, 2036)},
            }
        }
    )
    apply_trustees_2026_nawi_projection(tree, end_year=2060)
    apply_trustees_2026_price_projection(tree, end_year=2060)
    for path, tr_path in ((NAWI, _tr_nawi), (UPRATING, _tr_uprating)):
        for year in (2040, 2060):
            assert _value(tree, path, year) == pytest.approx(tr_path(year), rel=1e-12)
        for year in (2061, 2100, 2150):
            assert _value(tree, path, year) == _value(tree, path, 2060)


def _tree_with_reader(values, **uprating):
    return _small_tree(
        gov={
            "ssa": {
                "nawi": {"values": _series(NAWI, 2034)},
                "uprating": {"values": _series(UPRATING, 2036)},
                "reader": {
                    "values": values,
                    "metadata": {"uprating": {"parameter": UPRATING, **uprating}},
                },
            }
        }
    )


@pytest.mark.parametrize(
    "values, uprating, message",
    [
        ({"2028-01-01": 100}, {}, "states a value"),
        (
            {"2026-01-01": 100},
            {
                "at_defined_interval": {
                    "start": "0000-10-01",
                    "end": "0001-10-01",
                    "enactment": "0002-01-01",
                }
            },
            "cadence",
        ),
    ],
)
def test_a_reader_outside_the_rule_stops_the_assumption(values, uprating, message):
    tree = _tree_with_reader(values, **uprating)
    with pytest.raises(ValueError, match=message):
        apply_trustees_2026_path_readers(tree)


YEARS = st.integers(1990, 2150)


def _window(low, high):
    return st.integers(low, high - 1).flatmap(
        lambda start: st.tuples(st.just(start), st.integers(start + 1, high))
    )


PROPERTIES = settings(
    max_examples=50,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)


@PROPERTIES
@given(_window(2025, LAST_TABLE_YEAR), _window(2027, LAST_TABLE_YEAR))
def test_chain_identities_over_any_window(nawi_years, uprating_years):
    tree = _reformed()
    start, end = nawi_years
    assert _value(tree, NAWI, end) / _value(tree, NAWI, start) == pytest.approx(
        AWI[end] / AWI[start], rel=1e-12
    )
    start, end = uprating_years
    assert _value(tree, UPRATING, end) / _value(tree, UPRATING, start) == (
        pytest.approx(ACPI[end - 1] / ACPI[start - 1], rel=1e-12)
    )


@PROPERTIES
@given(_window(2015, 2150))
def test_cap_qc_threshold_and_bend_points_never_fall(years):
    tree = _reformed()
    start, end = years
    for path in (CAP, QC_THRESHOLD, BEND_POINT_1, BEND_POINT_2):
        assert _value(tree, path, start) <= _value(tree, path, end), path


@PROPERTIES
@given(st.sampled_from(TOUCHED), YEARS)
def test_applying_twice_equals_applying_once(path, year):
    assert _value(_reformed(), path, year) == _value(_applied_once(), path, year)


def _cap_policies():
    """A start year from 2027 to 2100 and a cap from the assumption's cap in
    that year up to no cap.

    The assumption re-extends the cap from 2028 on the no-decrease rule, so
    its second pass overwrites a policy cap that starts in 2028 or later. A
    policy from 2027 is the one that reaches the wage base through the
    second pass, so 2027 and no cap are drawn often.
    """
    years = st.one_of(st.just(2027), st.integers(2027, LAST_TABLE_YEAR))
    return years.flatmap(
        lambda year: st.tuples(
            st.just(year),
            st.one_of(
                st.just(math.inf),
                st.floats(
                    min_value=_statutory_path(CAP)[year],
                    allow_nan=False,
                    allow_infinity=True,
                ),
            ),
        )
    )


@PROPERTIES
@given(_cap_policies(), st.booleans())
@example(policy=(2027, math.inf), first=False)
@example(policy=(2027, math.inf), first=True)
def test_any_cap_only_policy_leaves_the_wage_base_and_the_copy(policy, first):
    """Replay both passes of the assumption and any cap-only policy, in
    either order: the wage base and the owners' draw copy keep the values
    the assumption alone gives them."""
    start_year, policy_cap = policy

    def apply_policy(parameters):
        get_parameter(parameters, CAP).update(
            start=f"{start_year}-01-01", value=policy_cap
        )

    reform_set = (apply_trustees_2026_economic_assumptions, apply_policy)
    if first:
        reform_set = reform_set[::-1]
    tree = _applied_once()
    expected = {path: _entries(tree, path) for path in (WAGE_BASE, OWNERS_DRAW_CAP)}
    with _on_default_values(tree):
        for apply in reform_set * 2:
            apply(tree)
        for path, entries in expected.items():
            assert _entries(tree, path) == entries, path


def test_real_wage_growth_matches_the_trustees_long_run():
    tree = _reformed()
    wages = _value(tree, NAWI, 2100) / _value(tree, NAWI, 2050)
    prices = _value(tree, UPRATING, 2100) / _value(tree, UPRATING, 2050)
    real_growth = 100 * ((wages / prices) ** (1 / 50) - 1)
    assert abs(real_growth - 1.13) <= 0.02


def _core_thresholds_under(reforms):
    parameters = CountryTaxBenefitSystem(reform=reforms).parameters
    nawi = {year: _value(parameters, NAWI, year) for year in range(2026, 2101)}
    thresholds = {
        parameter.name: {year: parameter(f"{year}-01-01") for year in range(2027, 2101)}
        for parameter in _iter_updatable_parameters(
            parameters.gov.irs, uprating_parameter="gov.irs.uprating"
        )
    }
    return nawi, thresholds


def _round_like_core_thresholds(amount, rounding):
    if not rounding:
        return amount
    if rounding["type"] == "downwards":
        return math.floor(amount / rounding["interval"]) * rounding["interval"]
    assert rounding["type"] == "nearest"
    return math.floor(amount / rounding["interval"] + 0.5) * rounding["interval"]


COMPOSITIONS = {
    "assumption_first": (
        trustees_2026_economic_assumptions_reform,
        trustees_core_thresholds_reform,
    ),
    "core_thresholds_first": (
        trustees_core_thresholds_reform,
        trustees_2026_economic_assumptions_reform,
    ),
}


@pytest.mark.parametrize("order", COMPOSITIONS)
def test_core_thresholds_follow_the_trustees_2026_nawi(order):
    """In either order, every IRS parameter the core-thresholds reform
    wage-indexes follows the Trustees' NAWI after 2034. A built system
    applies its reform set twice, so on the second pass the core-thresholds
    reform reads this assumption's NAWI whichever comes first.

    Last in the module: it frees the cached trees before building its own.
    """
    for cached in (_reformed_system, _applied_once, _end_to_end, _cap_policy_run):
        cached.cache_clear()
    nawi, thresholds = _core_thresholds_under(COMPOSITIONS[order])
    for year in range(2026, 2101):
        assert nawi[year] == pytest.approx(_tr_nawi(year), rel=1e-12)
    assert len(thresholds) > 100
    for path, values in thresholds.items():
        default = get_parameter(system.parameters, path)
        rounding = _rounding(default.metadata["uprating"])
        base = default("2034-01-01")
        for year, value in values.items():
            if year <= 2034:
                expected = default(f"{year}-01-01")
            else:
                expected = _round_like_core_thresholds(
                    base * (nawi[year - 1] / nawi[2033]), rounding
                )
            assert value == pytest.approx(expected, rel=1e-12), (path, year)
    for path in (
        "gov.irs.income.bracket.thresholds.1.SINGLE",
        "gov.irs.deductions.standard.amount.SINGLE",
    ):
        default = get_parameter(system.parameters, path)
        rounding = _rounding(default.metadata["uprating"])
        for year in (2035, 2060, 2100):
            on_default_nawi = _round_like_core_thresholds(
                default("2034-01-01")
                * _value(system.parameters, NAWI, year - 1)
                / _value(system.parameters, NAWI, 2033),
                rounding,
            )
            assert thresholds[path][year] != on_default_nawi
