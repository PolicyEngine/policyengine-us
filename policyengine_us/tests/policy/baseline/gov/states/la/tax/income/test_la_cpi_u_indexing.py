"""Louisiana's CPI-U-indexed standard deduction and retirement exemption.

La. R.S. 47:294(B) and 47:44.1(A) adjust the standard deduction and the
age-65 retirement income exemption each year by the prior calendar year's
CPI-U percentage increase. LDR Revenue Information Bulletin 26-019
(September 28, 2026) publishes the 2026 amounts, which are encoded in the
YAML; ``extend_la_cpi_u_indexed_amounts`` projects the later years.
"""

from fractions import Fraction
from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from policyengine_core.parameters import Parameter, ParameterNode
from policyengine_core.periods import instant

from policyengine_us.parameters.uprating_extensions import (
    adjust_la_amount_for_inflation,
    extend_la_cpi_u_indexed_amounts,
    get_la_cpi_u_percentage_increase,
    get_projected_cpi_u_for_month,
)
from policyengine_us.system import system

PARAMETERS = system.parameters
CPI = PARAMETERS.gov.bls.cpi
LA = PARAMETERS.gov.states.la.tax.income
STANDARD = LA.deductions.standard.amount
LAST_PUBLISHED_YEAR = 2026
END_YEAR = 2100


def retirement_cap(parameters, year):
    """The 65+ retirement income exemption cap, through the scale's calc."""
    la = parameters(f"{year}-01-01").gov.states.la.tax.income
    return float(la.exempt_income.retirement.cap.calc(np.array([65]))[0])


def test_reproduces_rib_26_019_from_2025_amounts():
    """The projection method recomputes every RIB 26-019 amount."""
    percentage = get_la_cpi_u_percentage_increase(CPI, 2025)
    assert percentage == 2.7
    single = adjust_la_amount_for_inflation(12_500, percentage)
    assert single == 12_838
    assert 2 * single == 25_676
    assert adjust_la_amount_for_inflation(12_000, percentage) == 12_324
    # The encoded 2026 values agree with the computation.
    for status in ("SINGLE", "SEPARATE"):
        assert getattr(STANDARD, status)("2026-01-01") == 12_838
    for status in ("JOINT", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"):
        assert getattr(STANDARD, status)("2026-01-01") == 25_676
    assert retirement_cap(PARAMETERS, 2026) == 12_324


def test_other_readings_do_not_reproduce_rib_26_019():
    """Pin the reading: BLS's rounded Dec-Dec change, doubled single amount."""
    # Unrounded December 2024 to December 2025 change (not seasonally
    # adjusted): $12,835, PolicyEngine's previous self-computed amount.
    unrounded = 100 * (324.054 / 315.605 - 1)
    assert adjust_la_amount_for_inflation(12_500, round(unrounded, 6)) == 12_835
    # The 2025 annual-average change, 321.943 / 313.689, rounds to 2.6%.
    assert round(100 * (321.943 / 313.689 - 1), 1) == 2.6
    assert adjust_la_amount_for_inflation(12_500, 2.6) == 12_825
    # Adjusting the joint amount on its own gives $25,675, not $25,676.
    assert adjust_la_amount_for_inflation(25_000, 2.7) == 25_675


def test_percentages_match_bls_published_december_changes():
    """The CPI-U 12-month changes BLS reported for each December."""
    published = {
        2013: 1.5,
        2014: 0.8,
        2015: 0.7,
        2016: 2.1,
        2017: 2.1,
        2018: 1.9,
        2019: 2.3,
        2020: 1.4,
        2021: 7.0,
        2022: 6.5,
        2023: 3.4,
        2024: 2.9,
        2025: 2.7,
    }
    for year, percentage in published.items():
        assert get_la_cpi_u_percentage_increase(CPI, year) == percentage, year


def synthetic_cpi(cpi_u, nsa_december=None):
    """A gov.bls.cpi node; the 1900 placeholder December matches no test year."""
    return SimpleNamespace(
        cpi_u=Parameter("cpi_u", data=cpi_u),
        cpi_u_nsa_december=Parameter(
            "cpi_u_nsa_december", data=nsa_december or {"1900-12-01": 1}
        ),
    )


def test_published_not_seasonally_adjusted_decembers_take_precedence():
    cpi = synthetic_cpi(
        cpi_u={"2029-12-01": 200, "2030-12-01": 205.2, "2031-12-01": 211},
        nsa_december={"2029-12-01": 200, "2030-12-01": 205.4},
    )
    # Both Decembers published: 205.4 / 200 = 2.7%, not the model series' 2.6%.
    assert get_la_cpi_u_percentage_increase(cpi, 2030) == 2.7
    # December 2031 is unpublished, so both Decembers come from the model
    # series rather than mixing the two: 211 / 205.2 = 2.83%.
    assert get_la_cpi_u_percentage_increase(cpi, 2031) == 2.8


def test_percentage_is_december_over_december_not_annual_average():
    monthly_2030 = {f"2030-{month:02d}-01": 200 + month for month in range(1, 12)}
    cpi = synthetic_cpi({"2029-12-01": 200, **monthly_2030, "2030-12-01": 205.4})
    # December to December: 205.4 / 200 = 2.7%. The 2030 annual average,
    # 206.2, would give 3.1%.
    assert get_la_cpi_u_percentage_increase(cpi, 2030) == 2.7


@pytest.mark.parametrize(
    "december, percentage",
    [
        (205.32, 2.7),  # 2.66% rounds up
        (205.28, 2.6),  # 2.64% rounds down
        (205.3, 2.7),  # exactly 2.65% rounds half up
        (200, 0),
        (195, 0),  # a fall in the index is not an increase
    ],
)
def test_percentage_rounds_to_one_decimal_and_never_falls_below_zero(
    december, percentage
):
    cpi = synthetic_cpi(
        cpi_u={"1900-01-01": 1},
        nsa_december={"2029-12-01": 200, "2030-12-01": december},
    )
    assert get_la_cpi_u_percentage_increase(cpi, 2030) == percentage


def test_unobserved_decembers_interpolate_toward_calendar_year_projections():
    cpi_u = Parameter(
        "cpi_u",
        data={
            "2030-12-01": 205,
            # Monthly observations end in June 2031.
            "2031-06-01": 210,
            # CBO calendar-year averages for 2032 and 2033.
            "2032-02-01": 220,
            "2033-02-01": 231,
        },
    )

    def level(month):
        return get_projected_cpi_u_for_month(cpi_u, instant(month))

    # Observed months read the series.
    assert level("2031-06-01") == 210
    # December 2031 is 6 of the 12.5 months from June 2031 to the 2032
    # average, placed between June and July 2032.
    assert level("2031-12-01") == pytest.approx(210 * (220 / 210) ** (6 / 12.5))
    # December 2032 is 5.5 of the 12 months between the 2032 and 2033
    # averages.
    assert level("2032-12-01") == pytest.approx(220 * (231 / 220) ** (5.5 / 12))
    # Past the last projection point the index holds flat.
    assert level("2033-12-01") == 231
    assert level("2040-12-01") == 231

    cpi = SimpleNamespace(
        cpi_u=cpi_u,
        cpi_u_nsa_december=Parameter("nsa", data={"1900-12-01": 1}),
    )
    # 2031: 214.742 / 205 = 4.75%. 2032: 224.975 / 214.742 = 4.77%.
    # 2033: 231 / 224.975 = 2.68%. 2034: 231 / 231.
    expected = {2031: 4.8, 2032: 4.8, 2033: 2.7, 2034: 0}
    for year, percentage in expected.items():
        assert get_la_cpi_u_percentage_increase(cpi, year) == percentage, year


def test_first_projected_year_gets_a_full_year_of_projected_inflation():
    """December 2026 is interpolated, not carried flat from June 2026."""
    cpi_u = CPI.cpi_u
    last_observation = max(
        instant(value.instant_str)
        for value in cpi_u.values_list
        if not value.instant_str.endswith("-02-01")
    )
    if last_observation >= instant("2026-12-01"):
        pytest.skip("December 2026 is observed")
    december_2026 = get_projected_cpi_u_for_month(cpi_u, instant("2026-12-01"))
    assert cpi_u(last_observation) < december_2026 < cpi_u("2027-02-01")


def last_observed_december(cpi_u):
    observed = [
        instant(value.instant_str)
        for value in cpi_u.values_list
        if not value.instant_str.endswith("-02-01")
    ]
    last = max(observed)
    return last.year if last.month == 12 else last.year - 1


def test_nsa_decembers_are_current_with_the_monthly_series():
    """Refreshing cpi_u past a December needs that December's NSA value."""
    newest_nsa = max(
        int(value.instant_str[:4]) for value in CPI.cpi_u_nsa_december.values_list
    )
    assert newest_nsa >= last_observed_december(CPI.cpi_u), (
        "Add the latest not seasonally adjusted December CPI-U (CUUR0000SA0) to "
        "gov/bls/cpi/cpi_u_nsa_december.yaml"
    )


@pytest.mark.parametrize("february", [190, 201.5, 260])
def test_february_in_the_last_observed_year_is_never_an_anchor(february):
    """Observations ending in January (or a February a refresh observed).

    The February instant may hold that year's projection or, after a
    refresh, an observation; neither may act as a calendar-year anchor, so
    its value cannot move any later month.
    """
    cpi_u = Parameter(
        "cpi_u",
        data={
            "2030-12-01": 200,
            "2031-01-01": 201,
            "2031-02-01": february,
            "2032-02-01": 211,
        },
    )
    # December 2031 is 11 of the 17.5 months from January 2031 to the 2032
    # average, placed between June and July 2032.
    assert get_projected_cpi_u_for_month(cpi_u, instant("2031-12-01")) == pytest.approx(
        201 * (211 / 201) ** (11 / 17.5)
    )


def synthetic_parameters(single_values, retirement_age=65):
    """A synthetic tree with the structure extend_la_cpi_u_indexed_amounts reads."""

    def doubled(values):
        return {date: 2 * value for date, value in values.items()}

    published = {"2025-01-01": 12_500, "2026-01-01": 12_838}
    income = ParameterNode(
        "income",
        data={
            "deductions": {
                "standard": {
                    "amount": {
                        "SINGLE": {"values": single_values},
                        "SEPARATE": {"values": published},
                        "JOINT": {"values": doubled(published)},
                        "HEAD_OF_HOUSEHOLD": {"values": doubled(published)},
                        "SURVIVING_SPOUSE": {"values": doubled(published)},
                    }
                }
            },
            "exempt_income": {
                "retirement": {
                    "cap": {
                        "brackets": [
                            {
                                "threshold": {"values": {"2021-01-01": 0}},
                                "amount": {"values": {"2021-01-01": 0}},
                            },
                            {
                                "threshold": {"values": {"2001-01-01": retirement_age}},
                                "amount": {
                                    "values": {
                                        "2001-01-01": 6_000,
                                        "2025-01-01": 12_000,
                                        "2026-01-01": 12_324,
                                    }
                                },
                            },
                        ],
                        "metadata": {"type": "single_amount"},
                    }
                }
            },
        },
    )
    cpi = synthetic_cpi(
        {
            "2025-12-01": 100,
            "2026-12-01": 102,
            "2027-12-01": 105,
            # Calendar-year 2028 projection; December 2028 is past it.
            "2028-02-01": 108,
        }
    )
    parameters = SimpleNamespace(
        gov=SimpleNamespace(
            bls=SimpleNamespace(cpi=cpi),
            states=SimpleNamespace(
                la=SimpleNamespace(tax=SimpleNamespace(income=income))
            ),
        )
    )
    return parameters, income


def test_extension_chains_from_published_amounts_and_doubles_the_single_amount():
    parameters, income = synthetic_parameters(
        {"2025-01-01": 12_500, "2026-01-01": 12_838}
    )
    extend_la_cpi_u_indexed_amounts(parameters, 2029)
    standard = income.deductions.standard.amount
    retirement = income.exempt_income.retirement.cap.brackets[1].amount
    # Published years keep their values.
    assert standard.SINGLE("2026-01-01") == 12_838
    assert retirement("2026-01-01") == 12_324
    # 2027: 102 / 100 = 2.0%. 12,838 x 1.02 = 13,094.76; 12,324 x 1.02 = 12,570.48.
    # 2028: 105 / 102 = 2.94%, so 2.9%. 13,095 x 1.029 = 13,474.755;
    # 12,570 x 1.029 = 12,934.53.
    # 2029: 108 / 105 = 2.86%, so 2.9%. 13,475 x 1.029 = 13,865.775;
    # 12,935 x 1.029 = 13,310.115.
    expected = {
        2027: (13_095, 12_570),
        2028: (13_475, 12_935),
        2029: (13_866, 13_310),
    }
    for year, (single, cap) in expected.items():
        assert standard.SINGLE(f"{year}-01-01") == single, year
        assert standard.SEPARATE(f"{year}-01-01") == single, year
        for status in ("JOINT", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"):
            assert getattr(standard, status)(f"{year}-01-01") == 2 * single, year
        assert retirement(f"{year}-01-01") == cap, year
    # The last projected amounts hold after the end year.
    assert standard.SINGLE("2040-01-01") == 13_866
    assert standard.JOINT("2040-01-01") == 27_732
    assert retirement("2040-01-01") == 13_310


def test_extension_requires_the_age_65_retirement_bracket():
    parameters, _ = synthetic_parameters(
        {"2025-01-01": 12_500, "2026-01-01": 12_838}, retirement_age=60
    )
    with pytest.raises(ValueError, match="age-65 bracket"):
        extend_la_cpi_u_indexed_amounts(parameters, 2029)


def test_extension_derives_other_statuses_from_an_encoded_single_amount():
    """A later published single amount is kept and the others follow it."""
    parameters, income = synthetic_parameters(
        {"2025-01-01": 12_500, "2026-01-01": 12_838, "2027-01-01": 13_000}
    )
    extend_la_cpi_u_indexed_amounts(parameters, 2029)
    standard = income.deductions.standard.amount
    assert standard.SINGLE("2027-01-01") == 13_000
    assert standard.SEPARATE("2027-01-01") == 13_000
    assert standard.JOINT("2027-01-01") == 26_000
    # 2028: 13,000 x 1.029 = 13,377. 2029: 13,377 x 1.029 = 13,764.933.
    assert standard.SINGLE("2028-01-01") == 13_377
    assert standard.HEAD_OF_HOUSEHOLD("2028-01-01") == 26_754
    assert standard.SINGLE("2029-01-01") == 13_765
    assert standard.SURVIVING_SPOUSE("2029-01-01") == 27_530


def projected_years():
    return range(LAST_PUBLISHED_YEAR + 1, END_YEAR + 1)


def test_projected_standard_deduction_follows_47_294():
    """Every projected year: 200% rule, whole dollars, statutory recurrence."""
    previous = STANDARD.SINGLE(f"{LAST_PUBLISHED_YEAR}-01-01")
    for year in projected_years():
        single = STANDARD.SINGLE(f"{year}-01-01")
        assert single == adjust_la_amount_for_inflation(
            previous, get_la_cpi_u_percentage_increase(CPI, year - 1)
        ), year
        assert single == int(single), year
        assert single >= previous, year
        assert STANDARD.SEPARATE(f"{year}-01-01") == single, year
        for status in ("JOINT", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"):
            assert getattr(STANDARD, status)(f"{year}-01-01") == 2 * single, year
        previous = single
    assert STANDARD.SINGLE("2150-01-01") == STANDARD.SINGLE(f"{END_YEAR}-01-01")


def test_projected_retirement_cap_follows_47_44_1():
    previous = retirement_cap(PARAMETERS, LAST_PUBLISHED_YEAR)
    for year in projected_years():
        cap = retirement_cap(PARAMETERS, year)
        assert cap == adjust_la_amount_for_inflation(
            previous, get_la_cpi_u_percentage_increase(CPI, year - 1)
        ), year
        assert cap == int(cap), year
        assert cap >= previous, year
        previous = cap
    # The under-65 bracket stays at zero.
    la = PARAMETERS(f"{END_YEAR}-01-01").gov.states.la.tax.income
    assert la.exempt_income.retirement.cap.calc(np.array([64]))[0] == 0


@pytest.mark.parametrize(
    "prior, percentage, adjusted",
    [
        # Half-dollar results that binary floating point misrounds:
        # prior x (1 + p / 100) gives 12,837 here.
        (12_500, 2.7, 12_838),
        # prior x (100 + p) / 100 gives 10,311 here.
        (10_250, 0.6, 10_312),
        # Both float forms give 20,725 here.
        (20_500, 1.1, 20_726),
        (12_000, 2.7, 12_324),
    ],
)
def test_adjustment_rounds_half_dollars_up_exactly(prior, percentage, adjusted):
    assert adjust_la_amount_for_inflation(prior, percentage) == adjusted


# One-decimal percentages, as BLS reports them.
percentages = st.integers(min_value=0, max_value=300).map(lambda tenths: tenths / 10)
amounts = st.integers(min_value=0, max_value=1_000_000)


@given(amounts, percentages)
def test_adjustment_rounds_to_the_nearest_dollar(prior, percentage):
    adjusted = adjust_la_amount_for_inflation(prior, percentage)
    exact = Fraction(prior) * (1 + Fraction(round(percentage * 10), 1_000))
    assert adjusted == int(adjusted)
    assert abs(Fraction(int(adjusted)) - exact) <= Fraction(1, 2)
    # Half dollars round up.
    if exact - int(exact) == Fraction(1, 2):
        assert adjusted == int(exact) + 1
    assert adjusted >= prior


@given(amounts, percentages, percentages)
def test_adjustment_is_monotone_in_the_percentage(prior, first, second):
    low, high = sorted((first, second))
    assert adjust_la_amount_for_inflation(prior, low) <= adjust_la_amount_for_inflation(
        prior, high
    )


@given(amounts)
def test_zero_percentage_keeps_the_amount(prior):
    assert adjust_la_amount_for_inflation(prior, 0) == prior


def nsa_cpi(prior_december, december):
    return synthetic_cpi(
        cpi_u={"1900-01-01": 1},
        nsa_december={"2029-12-01": prior_december, "2030-12-01": december},
    )


@given(
    st.floats(min_value=50, max_value=1_000),
    st.floats(min_value=0.8, max_value=1.3),
)
def test_percentage_is_the_rounded_nonnegative_change(prior_december, ratio):
    december = prior_december * ratio
    percentage = get_la_cpi_u_percentage_increase(
        nsa_cpi(prior_december, december), 2030
    )
    assert percentage >= 0
    assert round(percentage * 10) == pytest.approx(percentage * 10)
    change = 100 * (december / prior_december - 1)
    assert percentage == pytest.approx(max(change, 0), abs=0.05 + 1e-9)


@given(
    st.floats(min_value=50, max_value=1_000),
    st.floats(min_value=0.8, max_value=1.3),
    st.floats(min_value=0.8, max_value=1.3),
)
def test_percentage_is_monotone_in_the_december_index(prior_december, first, second):
    low, high = sorted((first, second))

    def percentage(ratio):
        return get_la_cpi_u_percentage_increase(
            nsa_cpi(prior_december, prior_december * ratio), 2030
        )

    assert percentage(low) <= percentage(high)


@given(
    st.floats(min_value=100, max_value=500),
    st.floats(min_value=1.0, max_value=1.1),
    st.floats(min_value=1.0, max_value=1.1),
    # A February instant would read as a projection point.
    st.integers(min_value=1, max_value=11).filter(lambda month: month != 2),
)
def test_interpolated_months_lie_between_their_anchors(
    observed, first_growth, second_growth, last_month
):
    first_point = observed * first_growth
    second_point = first_point * second_growth
    cpi_u = Parameter(
        "cpi_u",
        data={
            f"2030-{last_month:02d}-01": observed,
            "2031-02-01": first_point,
            "2032-02-01": second_point,
        },
    )
    previous = observed
    for year, month in [(2030, m) for m in range(last_month + 1, 13)] + [
        (2031, m) for m in range(1, 13)
    ]:
        level = get_projected_cpi_u_for_month(cpi_u, instant(f"{year}-{month:02d}-01"))
        assert observed <= level * (1 + 1e-12)
        assert level <= second_point * (1 + 1e-12)
        # Non-decreasing when the anchors are.
        assert level >= previous * (1 - 1e-12)
        previous = level
