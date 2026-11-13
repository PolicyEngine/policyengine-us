"""Growth splice of CBO's tax-year CPI projections onto BLS observations.

26 U.S.C. 1(f)(4) and (6)(B) index tax parameters to the average of a price
index over the 12 months ending August 31. The model averages BLS
observations while a window holds one. For each later window it multiplies
the last such average by CBO's projected growth in that 12-month average
(``get_average_for_12_months_ending_august`` in
``parameters/uprating_extensions.py``). These tests check four invariants:

1. every window with no observed month grows at CBO's projected rate for
   its tax year;
2. every window with an observed month averages the file's values, whatever
   the projection holds;
3. rescaling CBO's whole projection by a positive constant changes no index
   value;
4. an independent recomputation from the YAML files agrees with the model.

Each invariant runs on generated series and on the live ones.
"""

import math
from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_core.parameters import Parameter
from policyengine_core.periods import instant

from policyengine_us.parameters.uprating_extensions import (
    get_average_for_12_months_ending_august,
    get_cpi_u_average_for_12_months_ending_august,
    get_irs_cpi,
    get_vt_cpi,
)
from policyengine_us.system import system

PARAMETERS = system.parameters
CPI_DIRECTORY = Path(__file__).parents[4] / "parameters/gov/bls/cpi"
LAST_CBO_TAX_YEAR = 2036


def _next_month(month):
    year, number = month
    return (year + 1, 1) if number == 12 else (year, number + 1)


def _last_observation(observations):
    """The latest month with an observation.

    February instants after the observations hold CBO's calendar-year
    averages, so only other months mark where the observations end.
    """
    return max(month for month in observations if month[1] != 2)


def _last_observed_window(observations):
    """The last year whose 12 months ending August hold an observation."""
    year, number = _last_observation(observations)
    return year + 1 if number >= 9 else year


def _independent_index(observations, projection, year):
    """The index for the 12 months ending August of ``year``, from plain dicts.

    ``observations`` maps (year, month) to a level and ``projection`` maps a
    tax year to CBO's projected average for the 12 months ending the August
    before it.
    """
    last = _last_observation(observations)
    # Walk forward from the first observation to the last, carrying each
    # value into the months that have none.
    filled, month, level = {}, min(observations), None
    while month <= last:
        level = observations.get(month, level)
        filled[month] = level
        month = _next_month(month)

    def average(window_year):
        months = [(window_year - 1, number) for number in range(9, 13)]
        months += [(window_year, number) for number in range(1, 9)]
        assert months[0] >= min(observations)
        # Months after the last observation hold its level.
        return math.fsum(filled.get(month, filled[last]) for month in months) / 12

    base_year = _last_observed_window(observations)
    if year <= base_year:
        return average(year)
    return average(base_year) * projection[year + 1] / projection[base_year + 1]


def _monthly_parameter(observations):
    return Parameter(
        "cpi",
        data={
            f"{year}-{number:02d}-01": level
            for (year, number), level in observations.items()
        },
    )


def _projection_parameter(projection):
    return Parameter(
        "projection",
        data={f"{year}-01-01": level for year, level in projection.items()},
    )


LEVELS = st.floats(min_value=50, max_value=500)
FIRST_WINDOW = 2020


@st.composite
def generated_series(draw):
    """A monthly series from September 2019 and two tax-year projections.

    The series holds 12 to 48 months, loses up to three interior months (as
    the BLS series lost October 2025), and carries calendar-year points at
    later February instants. Each projection covers every tax year from 2020
    to ten years after the last observation.
    """
    count = draw(st.integers(min_value=12, max_value=48))
    months = [(2019, 9)]
    while len(months) < count:
        months.append(_next_month(months[-1]))
    levels = draw(st.lists(LEVELS, min_size=count, max_size=count))
    observations = dict(zip(months, levels))
    for month in draw(st.sets(st.sampled_from(months[1:-1]), max_size=3)):
        del observations[month]
    last_year = months[-1][0]
    first_projection_year = last_year if months[-1][1] == 1 else last_year + 1
    for year in range(first_projection_year, last_year + 4):
        observations[(year, 2)] = draw(LEVELS)
    tax_years = range(FIRST_WINDOW, last_year + 11)
    projections = [{year: draw(LEVELS) for year in tax_years} for _ in range(2)]
    return observations, projections[0], projections[1]


def _windows(observations):
    """Every window from the first full one to nine years past the series."""
    last_year = _last_observation(observations)[0]
    return range(FIRST_WINDOW, last_year + 9)


PROPERTY_SETTINGS = settings(
    max_examples=200, deadline=None, derandomize=True, database=None
)


@PROPERTY_SETTINGS
@given(series=generated_series())
def test_index_matches_an_independent_computation(series):
    observations, projection, _ = series
    cpi = _monthly_parameter(observations)
    cbo = _projection_parameter(projection)
    for year in _windows(observations):
        index = get_average_for_12_months_ending_august(cpi, year, cbo)
        expected = _independent_index(observations, projection, year)
        assert index == pytest.approx(expected, rel=1e-12), year


@PROPERTY_SETTINGS
@given(series=generated_series())
def test_windows_without_observations_grow_at_the_projected_rate(series):
    observations, projection, _ = series
    cpi = _monthly_parameter(observations)
    cbo = _projection_parameter(projection)
    first_unobserved = _last_observed_window(observations) + 1
    for year in range(first_unobserved, _windows(observations).stop):
        growth = get_average_for_12_months_ending_august(
            cpi, year, cbo
        ) / get_average_for_12_months_ending_august(cpi, year - 1, cbo)
        # ``year`` indexes tax year ``year + 1``.
        expected = projection[year + 1] / projection[year]
        assert growth == pytest.approx(expected, rel=1e-12), year


@PROPERTY_SETTINGS
@given(series=generated_series())
def test_windows_with_observations_ignore_the_projection(series):
    observations, projection, other_projection = series
    cpi = _monthly_parameter(observations)
    cbo = _projection_parameter(projection)
    other = _projection_parameter(other_projection)
    for year in range(FIRST_WINDOW, _last_observed_window(observations) + 1):
        index = get_average_for_12_months_ending_august(cpi, year, cbo)
        assert index == get_average_for_12_months_ending_august(cpi, year, other)
        assert index == get_average_for_12_months_ending_august(
            cpi, year, cbo, splice_on_growth=False
        )


@PROPERTY_SETTINGS
@given(
    series=generated_series(),
    scale=st.floats(min_value=0.001, max_value=1_000),
)
def test_rescaling_the_projection_changes_no_index_value(series, scale):
    observations, projection, _ = series
    cpi = _monthly_parameter(observations)
    cbo = _projection_parameter(projection)
    scaled = _projection_parameter(
        {year: level * scale for year, level in projection.items()}
    )
    for year in _windows(observations):
        assert get_average_for_12_months_ending_august(
            cpi, year, scaled
        ) == pytest.approx(
            get_average_for_12_months_ending_august(cpi, year, cbo), rel=1e-12
        ), year


@PROPERTY_SETTINGS
@given(series=generated_series())
def test_growth_and_level_splices_agree_when_the_projection_matches_the_base(
    series,
):
    """A projection that puts the last observed window at its observed average
    gives the same index whether the model applies its growth or its levels."""
    observations, projection, _ = series
    cpi = _monthly_parameter(observations)
    base_year = _last_observed_window(observations)
    base = get_average_for_12_months_ending_august(
        cpi, base_year, _projection_parameter(projection)
    )
    cbo = _projection_parameter({**projection, base_year + 1: base})
    for year in range(base_year + 1, _windows(observations).stop):
        assert get_average_for_12_months_ending_august(cpi, year, cbo) == pytest.approx(
            get_average_for_12_months_ending_august(
                cpi, year, cbo, splice_on_growth=False
            ),
            rel=1e-12,
        ), year


@PROPERTY_SETTINGS
@given(series=generated_series())
def test_level_splice_returns_the_projection(series):
    observations, projection, _ = series
    cpi = _monthly_parameter(observations)
    cbo = _projection_parameter(projection)
    first_unobserved = _last_observed_window(observations) + 1
    for year in range(first_unobserved, _windows(observations).stop):
        assert (
            get_average_for_12_months_ending_august(
                cpi, year, cbo, splice_on_growth=False
            )
            == projection[year + 1]
        )


def test_growth_splice_needs_a_projection_for_the_last_observed_window():
    # Observations run from September 2029 to August 2030, the window that
    # indexes tax year 2031. A projection that starts in 2032 gives no rate
    # of growth from that window.
    observations = {(2029, number): 100 for number in range(9, 13)}
    observations.update({(2030, number): 100 for number in range(1, 9)})
    cpi = _monthly_parameter(observations)
    cbo = _projection_parameter({2032: 104, 2033: 108})
    assert get_average_for_12_months_ending_august(cpi, 2030, cbo) == 100
    with pytest.raises(ValueError, match="tax year 2031"):
        get_average_for_12_months_ending_august(cpi, 2031, cbo)
    assert (
        get_average_for_12_months_ending_august(cpi, 2031, cbo, splice_on_growth=False)
        == 104
    )


# The live series: gov.bls.cpi and its tax_year_projection.


def _yaml_values(relative_path):
    return yaml.safe_load((CPI_DIRECTORY / relative_path).read_text())["values"]


def _yaml_observations(series):
    return {
        (date.year, date.month): float(level)
        for date, level in _yaml_values(f"{series}.yaml").items()
    }


def _yaml_projection(series):
    return {
        date.year: float(level)
        for date, level in _yaml_values(f"tax_year_projection/{series}.yaml").items()
    }


LIVE_SERIES = {
    "c_cpi_u": get_irs_cpi,
    "cpi_u": get_cpi_u_average_for_12_months_ending_august,
}


@pytest.mark.parametrize("series", sorted(LIVE_SERIES))
def test_recomputation_from_yaml_agrees_with_the_model(series):
    """Tax years 2018-2036, recomputed here from the two YAML files."""
    observations = _yaml_observations(series)
    projection = _yaml_projection(series)
    assert max(projection) == LAST_CBO_TAX_YEAR
    for tax_year in range(2018, LAST_CBO_TAX_YEAR + 1):
        expected = _independent_index(observations, projection, tax_year - 1)
        index = LIVE_SERIES[series](PARAMETERS, tax_year - 1)
        assert index == pytest.approx(expected, rel=1e-12), tax_year
        if series == "c_cpi_u":
            assert PARAMETERS.gov.irs.uprating(f"{tax_year}-01-01") == pytest.approx(
                expected, rel=1e-12
            ), tax_year


@pytest.mark.parametrize("series", sorted(LIVE_SERIES))
def test_live_index_grows_at_cbo_rates_after_the_last_observed_window(series):
    """Through 2036 the rates are CBO's; later years repeat the 2035-2036 rate."""
    base_tax_year = _last_observed_window(_yaml_observations(series)) + 1
    cbo = _yaml_projection(series)
    terminal = cbo[LAST_CBO_TAX_YEAR] / cbo[LAST_CBO_TAX_YEAR - 1]
    for tax_year in range(base_tax_year + 1, 2101):
        growth = LIVE_SERIES[series](PARAMETERS, tax_year - 1) / LIVE_SERIES[series](
            PARAMETERS, tax_year - 2
        )
        if tax_year <= LAST_CBO_TAX_YEAR:
            expected = cbo[tax_year] / cbo[tax_year - 1]
        else:
            expected = terminal
        assert growth == pytest.approx(expected, rel=1e-12), tax_year


@pytest.mark.parametrize("series", sorted(LIVE_SERIES))
def test_live_observed_windows_ignore_the_projection(series):
    cpi = getattr(PARAMETERS.gov.bls.cpi, series)
    projection = getattr(PARAMETERS.gov.bls.cpi.tax_year_projection, series)
    other = Parameter("other", data={"2000-01-01": 1})
    last_observed_window = _last_observed_window(_yaml_observations(series))
    for year in range(2009, last_observed_window + 1):
        index = get_average_for_12_months_ending_august(cpi, year, projection)
        assert index == get_average_for_12_months_ending_august(cpi, year, other)
        assert index == get_average_for_12_months_ending_august(
            cpi, year, projection, splice_on_growth=False
        )


@pytest.mark.parametrize("series", sorted(LIVE_SERIES))
@settings(max_examples=50, deadline=None, derandomize=True, database=None)
@given(scale=st.floats(min_value=0.001, max_value=1_000))
def test_rescaling_cbo_projection_changes_no_live_index_value(series, scale):
    cpi = getattr(PARAMETERS.gov.bls.cpi, series)
    projection = getattr(PARAMETERS.gov.bls.cpi.tax_year_projection, series)
    scaled = Parameter(
        "scaled",
        data={
            value.instant_str: value.value * scale for value in projection.values_list
        },
    )
    for year in range(2025, LAST_CBO_TAX_YEAR + 5):
        assert get_average_for_12_months_ending_august(
            cpi, year, scaled
        ) == pytest.approx(
            get_average_for_12_months_ending_august(cpi, year, projection),
            rel=1e-12,
        ), year


def test_vermont_index_takes_cbo_levels_for_windows_without_observations():
    """32 V.S.A. 5811 and 5822 windows past the last observation read CBO's
    projected national average as a level."""
    cpi = PARAMETERS.gov.bls.cpi
    last = max(
        instant(value.instant_str)
        for value in cpi.cpi_u_nsa.values_list
        if not value.instant_str.endswith("-02-01")
    )
    last_observed_tax_year = last.year + int(last.month >= 9) + 1
    assert get_vt_cpi(
        PARAMETERS, last_observed_tax_year
    ) != cpi.tax_year_projection.cpi_u(f"{last_observed_tax_year}-01-01")
    for tax_year in range(last_observed_tax_year + 1, LAST_CBO_TAX_YEAR + 1):
        assert get_vt_cpi(PARAMETERS, tax_year) == cpi.tax_year_projection.cpi_u(
            f"{tax_year}-01-01"
        )
