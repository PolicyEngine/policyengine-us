"""Signed allocation properties and multi-year S.770 reform integration.

The inexpensive Hypothesis cases exercise vector helpers without rebuilding
the model. One shared, read-only simulation then checks registration, changing
switches/start years, entity aggregation and revenue accounting across years;
YAML cannot express those dated parameter changes. No population data are used.
Direct-NII YAML cases cover the NOL-denial hook separately from these source
aggregation checks.

Unified-liability equivalence assumes identical signed sources, exclusions,
NOL treatment, MAGI, thresholds and timing, with existing rate + add-on rate =
active rate = 16.2%. It does not imply equal OASDI transfers or full statutory
category coverage. Adding a signed active loss can lower total tax, so the
monotonicity property requires a nonnegative active residual and fixed signed
NII/source rules, including exclusions and NOL treatment, across switches.
Activating an exclusion can lower existing NIIT even with a nonnegative active
residual; YAML pins that separate source-classification counterexample.
"""

from types import SimpleNamespace

import numpy as np
import pytest

from policyengine_core.reforms import Reform
from policyengine_us import Simulation
from policyengine_us.reforms.congress.s770.section_8 import (
    active_residual,
    allocate_bases,
    enabled,
    transfer_shares,
)

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

EXISTING_RATE = 0.038
ADDON_RATE = 0.124
ACTIVE_RATE = 0.162
SHARE = 0.62
YEARS = tuple(range(2025, 2035))
MODES = ("custom", "bill", "combined_rate_share", "all_addon")
SETTINGS = hypothesis.settings(max_examples=100, deadline=None)
SIGNED = st.integers(-1_000_000, 1_000_000)
NONNEGATIVE = st.integers(0, 1_000_000)
BASES = st.lists(st.tuples(SIGNED, SIGNED, NONNEGATIVE), min_size=1, max_size=30)


@SETTINGS
@hypothesis.given(BASES)
def test_signed_unified_liability_equivalence(rows):
    nii, active, excess = np.asarray(rows, dtype=float).T
    n, a = allocate_bases(nii, active, excess)
    unified = np.minimum(np.maximum(nii + active, 0), excess)
    total = EXISTING_RATE * n + ADDON_RATE * n + ACTIVE_RATE * a
    np.testing.assert_allclose(total, ACTIVE_RATE * unified, atol=1e-8)
    np.testing.assert_allclose(n + a, unified)
    assert np.all(total >= 0)
    assert np.all(n >= 0)
    assert np.all(a >= 0)
    assert np.all(n <= np.maximum(nii, 0))
    # Signed sources are netted first; the resulting allocated shares are
    # both nonnegative under E2's allocation, even when a source is negative.
    np.testing.assert_allclose(a[n < np.maximum(nii, 0)], 0)


def test_review_counterexamples_and_zero_addon_threshold_allocation():
    n, a = allocate_bases(
        np.array([-10_000, 20_000, 20_000]),
        np.array([20_000, -10_000, 20_000]),
        np.array([50_000, 50_000, 30_000]),
    )
    np.testing.assert_array_equal(n, [0, 10_000, 20_000])
    np.testing.assert_array_equal(a, [10_000, 0, 10_000])
    np.testing.assert_allclose(ACTIVE_RATE * (n + a), [1_620, 1_620, 4_860])
    assert EXISTING_RATE * n[2] + ACTIVE_RATE * a[2] == pytest.approx(2_380)
    # An active loss reduces the existing 3.8% component as well as the
    # add-on; unconditional monotonicity would contradict signed netting.
    assert ACTIVE_RATE * (n[1] + a[1]) < ACTIVE_RATE * 20_000


@SETTINGS
@hypothesis.given(nii=SIGNED, active=NONNEGATIVE, excess=NONNEGATIVE)
def test_turning_on_parts_is_monotone_with_fixed_nii_and_nonnegative_active_income(
    nii, active, excess
):
    # The signed NII input is fixed across switches. Applying new SECA/FICA
    # source exclusions when the active option starts is outside this property.
    n, a = allocate_bases(nii, active, excess)
    n_without_active, _ = allocate_bases(nii, 0, excess)
    baseline = EXISTING_RATE * n_without_active
    addon_only = (EXISTING_RATE + ADDON_RATE) * n_without_active
    active_only = EXISTING_RATE * n + ACTIVE_RATE * a
    both = (EXISTING_RATE + ADDON_RATE) * n + ACTIVE_RATE * a
    assert addon_only >= baseline
    assert active_only >= baseline
    assert both >= addon_only
    assert both >= active_only


@SETTINGS
@hypothesis.given(
    active=NONNEGATIVE,
    passive=NONNEGATIVE,
    already_se=NONNEGATIVE,
    draw_exclusion=NONNEGATIVE,
)
def test_no_profit_is_in_both_seca_and_active_residual(
    active, passive, already_se, draw_exclusion
):
    # Disjoint source subsets are drawn independently. The two SECA-covered
    # subsets leave exactly the undrawn, nonpassive active dollars behind.
    total = active + passive + already_se + draw_exclusion
    residual = active_residual(total, passive, already_se, draw_exclusion)
    assert residual == active
    assert residual + already_se + draw_exclusion == total - passive


@SETTINGS
@hypothesis.given(total=SIGNED, passive=SIGNED, already_se=SIGNED)
def test_active_residual_preserves_signed_losses(total, passive, already_se):
    assert active_residual(total, passive, already_se) + passive + already_se == total


@SETTINGS
@hypothesis.given(
    mode=st.sampled_from(MODES),
    nii_share=st.integers(0, 10_000),
    active_share=st.integers(0, 10_000),
    bill_share=st.integers(0, 10_000),
    nii_tax=NONNEGATIVE,
    addon_tax=NONNEGATIVE,
    active_tax=NONNEGATIVE,
)
def test_transfer_modes_account_for_each_component(
    mode, nii_share, active_share, bill_share, nii_tax, addon_tax, active_tax
):
    nii_share, active_share, bill_share = (
        value / 10_000 for value in (nii_share, active_share, bill_share)
    )
    shares = transfer_shares(
        mode,
        EXISTING_RATE,
        ADDON_RATE,
        ACTIVE_RATE,
        nii_share,
        active_share,
        bill_share,
        ADDON_RATE,
    )
    expected = {
        "custom": (0, nii_share, active_share),
        "bill": (bill_share,) * 3,
        "combined_rate_share": (ADDON_RATE / ACTIVE_RATE,) * 3,
        "all_addon": (0, 1, active_share),
    }[mode]
    np.testing.assert_allclose(shares, expected)
    taxes = np.array([nii_tax, addon_tax, active_tax])
    np.testing.assert_allclose(np.asarray(shares) * taxes, np.asarray(expected) * taxes)
    if mode == "bill":
        assert np.dot(shares, taxes) == pytest.approx(bill_share * taxes.sum())


def test_combined_rate_transfer_handles_zero_rates():
    assert transfer_shares("combined_rate_share", 0, 0, 0, SHARE, SHARE, SHARE, 0) == (
        0,
        0,
        0,
    )


@SETTINGS
@hypothesis.given(
    in_effect=st.booleans(),
    start_year=st.integers(2026, 2040),
    year=st.integers(2020, 2045),
)
def test_activation_requires_switch_and_start_year(in_effect, start_year, year):
    part = SimpleNamespace(in_effect=in_effect, start_year=start_year)
    period = SimpleNamespace(start=SimpleNamespace(year=year))
    assert bool(enabled(part, period)) == (in_effect and year >= start_year)


class DatedSection8Options(Reform):
    """Exercise the public parameter route, including structural registration."""

    def apply(self):
        def modify(parameters):
            p = parameters.gov.contrib.congress.s770.section_8
            for year in YEARS:
                values = {
                    "nii_addon.in_effect": year not in (2027, 2033),
                    "active_business.in_effect": year not in (2026, 2033),
                    "nii_addon.start_year": 2026,
                    "active_business.start_year": 2026,
                    "nii_addon.rate": 0 if year == 2032 else ADDON_RATE,
                    "active_business.rate": ACTIVE_RATE,
                    "nii_addon.oasdi_share": SHARE,
                    "active_business.oasdi_share": SHARE,
                    "transfer.mode": {
                        2029: 3,
                        2030: 1,
                        2031: 2,
                    }.get(year, 0),
                    "transfer.start_year": 2035 if year == 2034 else 2026,
                    "transfer.bill_share": SHARE,
                    "transfer.oasdi_rate": ADDON_RATE,
                }
                for path, value in values.items():
                    node = p
                    for key in path.split("."):
                        node = getattr(node, key)
                    node.update(period=str(year), value=value)
            return parameters

        self.modify_parameters(modify)


# Each row is a separate tax unit. Derived MAGI is deliberately used instead
# of entering niit_magi, and dependent income must not join the filer's bases.
ROWS = [
    dict(rental=-10_000, total=20_000),
    dict(rental=20_000, total=-10_000),
    dict(rental=20_000, total=20_000, agi=230_000),
    dict(total=30_000, passive=10_000, already_se=10_000),
    dict(total=30_000, passive=10_000, already_se=15_000, overlap=5_000),
    dict(rental=20_000, total=30_000, fica=10_000, nii_fica=5_000),
    dict(total=100_000, draw=80_000, draw_base=9_235),
    dict(total=100_000, draw=80_000, draw_base=9_235, hi=True),
    dict(rental=20_000, total=20_000, agi=230_000, dependent=True),
    dict(
        rental=15_000, total=20_000, agi=180_000, estate_adjustment=20_000, feie=10_000
    ),
    dict(rental=5_000, total=5_000, spouse=True),
]


def _situation():
    people, tax_units, households = {}, {}, {}

    def annual(value):
        return {str(year): value for year in YEARS}

    for i, row in enumerate(ROWS):
        head = f"head_{i}"
        people[head] = {
            "age": annual(45),
            "is_tax_unit_head": annual(True),
            "rental_income": annual(row.get("rental", 0)),
            "s_corp_income": annual(row.get("total", 0) / 2),
            "partnership_income": annual(row.get("total", 0) / 2),
            "passive_partnership_s_corp_income": annual(row.get("passive", 0)),
            "partnership_self_employment_net_earnings": annual(
                row.get("already_se", 0)
            ),
            "s770_passive_se_income": annual(row.get("overlap", 0)),
            "s770_active_fica_income": annual(row.get("fica", 0)),
            "s770_draw_gross": annual(row.get("draw", 0)),
            "s770_draw_oasdi_base": annual(row.get("draw_base", 0)),
            "s770_draw_hi_in_effect": annual(row.get("hi", False)),
            "estate_income_niit_magi_adjustment": annual(
                row.get("estate_adjustment", 0)
            ),
        }
        members = [head]
        if row.get("dependent"):
            child = f"child_{i}"
            members.append(child)
            people[child] = {
                "age": annual(12),
                "is_tax_unit_dependent": annual(True),
                "rental_income": annual(1_000_000),
                "s_corp_income": annual(1_000_000),
            }
        if row.get("spouse"):
            spouse = f"spouse_{i}"
            members.append(spouse)
            people[spouse] = {
                "age": annual(45),
                "is_tax_unit_spouse": annual(True),
                "rental_income": annual(7_000),
                "s_corp_income": annual(11_000),
            }
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "filing_status": annual("JOINT" if row.get("spouse") else "SINGLE"),
            "adjusted_gross_income": annual(row.get("agi", 250_000)),
            "niit_magi_section_911_addition": annual(row.get("feie", 0)),
            "s770_nii_fica_seca_income": annual(row.get("nii_fica", 0)),
        }
        households[f"household_{i}"] = {"members": members, "state_code": annual("TX")}
    return {"people": people, "tax_units": tax_units, "households": households}


@pytest.fixture(scope="module")
def dated_simulation():
    # One full construction for all integration assertions, without mutation
    # after calculations begin. This fixture belongs to Rest's remaining group.
    return Simulation(
        situation=_situation(), reform=DatedSection8Options, start_instant="2025-01-01"
    )


@pytest.mark.parametrize("year", YEARS)
def test_dated_registration_components_and_revenue_accounts(dated_simulation, year):
    sim = dated_simulation
    nii_on = year >= 2026 and year not in (2027, 2033)
    active_on = year >= 2026 and year not in (2026, 2033)
    addon_rate = 0 if year == 2032 else ADDON_RATE
    expected_nii, expected_active, expected_excess = [], [], []
    for row in ROWS:
        nii = row.get("rental", 0) + row.get("passive", 0)
        active = row.get("total", 0) - row.get("passive", 0)
        active -= row.get("already_se", 0) - row.get("overlap", 0)
        active -= row.get("fica", 0)
        active -= (
            row.get("draw", 0)
            if row.get("hi", False)
            else row.get("draw_base", 0) / 0.9235
        )
        if row.get("spouse"):
            nii += 7_000
            active += 11_000
        if active_on:
            nii -= row.get("overlap", 0) + row.get("nii_fica", 0)
        expected_nii.append(nii)
        expected_active.append(active)
        threshold = 250_000 if row.get("spouse") else 200_000
        magi = (
            row.get("agi", 250_000)
            + row.get("estate_adjustment", 0)
            + row.get("feie", 0)
        )
        expected_excess.append(max(magi - threshold, 0))
    expected_nii = np.asarray(expected_nii)
    expected_active = np.asarray(expected_active)
    unified = np.minimum(
        np.maximum(expected_nii + (expected_active if active_on else 0), 0),
        expected_excess,
    )
    n = np.minimum(np.maximum(expected_nii, 0), unified)
    a = unified - n
    existing_tax = EXISTING_RATE * n
    addon_tax = addon_rate * n if nii_on else np.zeros_like(n)
    active_tax = ACTIVE_RATE * a if active_on else np.zeros_like(a)
    np.testing.assert_allclose(
        sim.calculate("s770_nii_base", year), expected_nii, atol=0.01
    )
    np.testing.assert_allclose(
        sim.calculate("s770_active_business_income", year), expected_active, atol=0.01
    )
    np.testing.assert_allclose(
        sim.calculate("s770_nii_taxable_base", year), n, atol=0.01
    )
    np.testing.assert_allclose(
        sim.calculate("s770_active_taxable_base", year), a, atol=0.01
    )
    for variable, expected in (
        ("s770_nii_addon_tax", addon_tax),
        ("s770_active_business_income_tax", active_tax),
        ("net_investment_income_tax", existing_tax + addon_tax + active_tax),
    ):
        actual = sim.calculate(variable, year)
        np.testing.assert_allclose(actual, expected, atol=0.01)
        assert np.all(actual >= 0)
    if year == 2029:
        shares = (SHARE,) * 3
    elif year == 2030:
        shares = (ADDON_RATE / ACTIVE_RATE,) * 3
    elif year == 2031:
        shares = (0, 1, SHARE)
    else:
        shares = (0, SHARE, SHARE)
    if year in (2025, 2033, 2034):
        shares = (0, 0, 0)
    revenues = []
    for variable, share, tax in zip(
        (
            "s770_existing_niit_revenue_oasdi",
            "s770_nii_addon_revenue_oasdi",
            "s770_active_business_income_revenue_oasdi",
        ),
        shares,
        (existing_tax, addon_tax, active_tax),
    ):
        revenue = sim.calculate(variable, year)
        np.testing.assert_allclose(revenue, share * tax, atol=0.01)
        revenues.append(revenue)
    np.testing.assert_allclose(
        sim.calculate("s770_revenue_oasdi", year), sum(revenues), atol=0.01
    )
