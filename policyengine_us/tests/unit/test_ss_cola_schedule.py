"""COLA timing, statutory rounding, projections and inverse intervals.

Published examples are cited at their assertions.  These tests exercise gross
monthly recurring benefits and exclude Medicare deductions and 2001 arrears.
"""

from decimal import Decimal, ROUND_FLOOR
from fractions import Fraction

import pytest
from hypothesis import given, settings, strategies as st

from policyengine_us import Simulation
from policyengine_us.tools.social_security.cola import (
    ColaEvent,
    adjusted_events,
    apply_colas,
    cola_factor,
    projected_events,
    read_parameter_events,
    reverse_colas_interval,
)


D = Decimal


@pytest.fixture(scope="module")
def parameters():
    return Simulation.default_tax_benefit_system_instance.parameters


def test_ssa_published_cola_application():
    # https://www.ssa.gov/oact/COLA/colaapplic.html
    event = ColaEvent("2011-12", "2012-01", D(".036"))
    assert apply_colas("2197.50", 2011, "2012-01", [event]) == D("2276.60")


def test_ssa_supplement_sequential_cola_example():
    # https://www.ssa.gov/policy/docs/statcomps/supplement/2023/apnd.html
    # This published arithmetic illustration deliberately uses a hypothetical
    # 2020 benchmark with a separately illustrated PIA; it is not an E2023 PIA.
    events = [
        ColaEvent("2020-12", "2021-01", D(".013")),
        ColaEvent("2021-12", "2022-01", D(".059")),
        ColaEvent("2022-12", "2023-01", D(".087")),
    ]
    assert apply_colas("1606.70", 2020, "2021-01", events) == D("1627.50")
    assert apply_colas("1606.70", 2020, "2022-01", events) == D("1723.50")
    assert apply_colas("1606.70", 2020, "2023-01", events) == D("1873.40")


def test_eligibility_colas_accrue_before_claiming_and_start_next_january():
    events = [ColaEvent("1983-12", "1984-01", D(".035"))]
    assert apply_colas("1000", 1983, "1983-12", events) == D("1000")
    assert apply_colas("1000", 1983, "1984-01", events) == D("1035")
    assert apply_colas("1000", 1984, "1984-01", events) == D("1000")


def test_truncates_after_every_cola_and_retains_raw_diagnostic():
    events = [
        ColaEvent("2020-12", "2021-01", D(".1")),
        ColaEvent("2021-12", "2022-01", D(".1")),
    ]
    assert apply_colas(".9", 2020, "2022-01", events) == D(".9")
    assert cola_factor(2020, "2022-01", events) == D("1.21")
    assert apply_colas(0, 2020, "2022-01", events) == 0


@pytest.mark.parametrize("year", [1979, 1982])
def test_rejects_unsupported_benchmarks_even_without_exposed_colas(year):
    with pytest.raises(ValueError, match="1983"):
        apply_colas(1000, year, "2026-01", [])
    with pytest.raises(ValueError, match="1983"):
        reverse_colas_interval(1000, 1001, year, "2026-01", [])


def test_rejects_unsupported_exposed_rounding_rule():
    event = ColaEvent("1983-12", "1984-01", D(".035"), "dime_ceiling")
    with pytest.raises(ValueError, match="rounding"):
        apply_colas(1000, 1983, "1984-01", [event])


def test_cola_changes_and_withholding_are_joint_and_preserve_precision():
    baseline = [
        ColaEvent("2026-12", "2027-01", D(".02")),
        ColaEvent("2027-12", "2028-01", D(0)),
        ColaEvent("2028-12", "2029-01", D(".01")),
    ]
    adjusted = adjusted_events(
        baseline,
        {2027: D(".0015"), 2028: D("-.003"), 2029: D(".0015")},
        withheld_years=[2029],
    )
    assert [event.rate for event in adjusted] == [D(".0215"), D(0), D(0)]
    assert apply_colas(1000, 2026, "2029-01", adjusted) == D("1021.5")


def test_projection_uses_statutory_rounding_and_retains_high_water():
    events = projected_events({2025: D("308.729"), 2026: D("317.265")})
    assert events[0].rate == D(".028")
    # Half-up at .05 percentage point; ties-to-even would incorrectly be zero.
    assert projected_events({2025: 100, 2026: D("100.05")})[0].rate == D(".001")
    events = projected_events({2025: 100, 2026: 99, 2027: D("100.04"), 2028: 101})
    assert [event.rate for event in events] == [D(0), D(0), D(".010")]


def test_projection_rejects_missing_or_invalid_q3_path():
    with pytest.raises(ValueError, match="consecutive"):
        projected_events({2025: 100, 2027: 101})
    with pytest.raises(ValueError, match="positive"):
        projected_events({2025: 0, 2026: 101})


def test_audited_history_timing_corrected_1999_and_future_horizon(parameters):
    # https://www.ssa.gov/OACT/COLA/colaseries.html
    canonical = parameters("2025-12-01").gov.ssa.cola_history
    assert D(str(canonical.rate)) == D(".028")
    assert canonical.effective_month == 12
    assert canonical.first_payment_month == 1
    assert canonical.pia_rounding == 2
    assert parameters("1981-06-01").gov.ssa.cola_history.pia_rounding == 1
    assert parameters("1982-06-01").gov.ssa.cola_history.pia_rounding == 2
    events = read_parameter_events(parameters, 2059)
    by_effective = {event.effective_month: event for event in events}
    assert by_effective["1975-06"].payment_month == "1975-07"
    assert by_effective["1982-06"].payment_month == "1982-07"
    assert by_effective["1983-12"].payment_month == "1984-01"
    assert by_effective["1999-12"].rate == D(".025")
    assert by_effective["1999-12"].as_paid_rate == D(".024")
    assert by_effective["2026-12"].rate == D(".036")
    assert by_effective["2058-12"].payment_month == "2059-01"
    assert apply_colas("1000", 2057, "2059-01", events) >= D("1000")


def test_canonical_history_stops_before_projected_2027_check(parameters):
    # Canonical authored history ends December2025. January2027 uses runtime
    # Q3 levels317.265 and328.746, giving a statutory rounded rate3.6%.
    assert (
        str(parameters.gov.ssa.cola_history.rate.metadata["historical_end"])
        == "2025-12-01"
    )
    events = read_parameter_events(parameters, 2027)
    projected = next(event for event in events if event.payment_month == "2027-01")
    assert projected.effective_month == "2026-12"
    assert projected.rate == D(".036")


def test_projection_explicitly_rejects_after_runtime_frozen_horizon(parameters):
    with pytest.raises(ValueError, match="frozen Q3 horizon 2100"):
        read_parameter_events(parameters, 2101)


def test_december_1999_original_checks_and_july_2001_correction(parameters):
    # https://secure.ssa.gov/poms.nsf/lnx/0300601122
    # The corrected July2001 PIA reconstructs the two prior COLAs, with dime
    # truncation after each. Original 2000 checks remain the amounts paid.
    events = read_parameter_events(parameters, 2002)
    assert apply_colas(1000, 1999, "2000-01", events) == D("1024")
    assert apply_colas(1000, 1999, "2001-07", events) == D("1059.8")
    assert apply_colas(1000, 1999, "2001-08", events) == D("1060.8")
    # An E2000 worker receives no December1999 correction.
    assert apply_colas(1000, 2000, "2001-08", events) == D("1035")


def test_historical_bend_points_are_separate_from_legacy_scale(parameters):
    # https://www.ssa.gov/OACT/COLA/bendpoints.html
    for year, expected in [
        (1979, (180, 1085)),
        (1983, (254, 1528)),
        (2000, (531, 3202)),
        (2026, (1286, 7749)),
    ]:
        bp = parameters(f"{year}-01-01").gov.ssa.social_security.pia.bend_points
        assert (bp.first, bp.second) == expected
    for year in range(2015, 2027):
        pia = parameters(f"{year}-01-01").gov.ssa.social_security.pia
        assert list(pia.formula_factors.thresholds)[1:] == [
            pia.bend_points.first,
            pia.bend_points.second,
        ]


@settings(max_examples=60, deadline=None)
@given(
    pia_dimes=st.integers(min_value=0, max_value=500_000),
    rates=st.lists(st.integers(min_value=0, max_value=100), min_size=0, max_size=5),
)
def test_reverse_cola_interval_exactly_contains_possible_dime_pias(pia_dimes, rates):
    pia = D(pia_dimes) / 10
    events = [
        ColaEvent(f"{2020 + i}-12", f"{2021 + i}-01", D(rate) / 1000)
        for i, rate in enumerate(rates)
    ]
    current = apply_colas(pia, 2020, "2026-01", events)
    check = current.quantize(D(1), rounding=ROUND_FLOOR)
    lower, upper = reverse_colas_interval(check, check + 1, 2020, "2026-01", events)
    assert lower <= pia < upper
    assert check <= apply_colas(lower, 2020, "2026-01", events) < check + 1
    assert apply_colas(upper, 2020, "2026-01", events) >= check + 1
    if lower >= D(".1"):
        assert apply_colas(lower - D(".1"), 2020, "2026-01", events) < check


def test_reverse_cola_interval_rejects_unattainable_payment():
    event = ColaEvent("2020-12", "2021-01", D(1))
    with pytest.raises(ValueError, match="no eligible PIA"):
        reverse_colas_interval(".1", ".2", 2020, "2021-01", [event])


def test_reverse_cola_interval_accepts_exact_nonterminating_ratio_endpoints():
    event = ColaEvent("2020-12", "2021-01", D(".1"))
    assert reverse_colas_interval(
        Fraction(1, 3), Fraction(2, 3), 2020, "2021-01", [event]
    ) == (D(".4"), D(".7"))
    # A rational endpoint immediately above a dime must not round down to that
    # dime when a Decimal context cannot retain all of its significant digits.
    precise_lower = Fraction(10**50 + 1, 10**51)
    assert reverse_colas_interval(
        precise_lower, Fraction(3, 10), 2020, "2021-01", []
    ) == (D(".2"), D(".3"))


def test_cola_truncation_preserves_exact_boundary_at_high_rate_precision():
    just_below_ten_percent = D("0." + "0" + "9" * 49)
    event = ColaEvent("2020-12", "2021-01", just_below_ten_percent)
    # 1*(1+.0999...) is strictly below1.1 even beyond Decimal's context.
    assert apply_colas(1, 2020, "2021-01", [event]) == D("1.0")
