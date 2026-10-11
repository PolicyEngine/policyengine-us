"""Functional forms for the capital gains realization response.

``f(tau0, tau1)`` is the response factor: realizations after the response are
the pre-response gains times the multiplier ``1 + f``. The properties below
hold for every input Hypothesis draws, within the stated domains:

1. No rate change, no response: ``f(tau, tau) == 0`` for every form, parameter
   and rate, including rates outside [0, 1].
2. Monotonicity: with a log-rate elasticity <= 0 and the new forms' parameters
   >= 0, the multiplier is non-increasing in the reform rate, and strictly
   decreasing inside each form's unclipped range when the parameter is nonzero
   and the multiplier resolves the step.
3. Sign preservation: ``1 + f >= 0``, so the response never flips the sign of
   a person's gains, and in the model's float32 arithmetic the new forms'
   dollar responses stay finite and sign-preserving across their supported
   parameter domains for any gains below $10 quadrillion.
4. Path independence: ``(1 + f(t0, t1)) * (1 + f(t1, t2)) == 1 + f(t0, t2)``
   to 1e-9 in float64 where each multiplier is at least 1e-6.
5. Single-rate revenue: ``tau * (1 + f(tau0, tau))`` peaks at ``1 / beta`` under
   the semi-elasticity form for beta > 1 and at ``1 / (1 + e)`` under the
   net-of-tax form for e >= 0.003, whatever the baseline rate, up to the
   rounding of a multiplier near 0. Under the log-rate form with an
   elasticity between -1 and 0 it rises all the way to a 100% rate.
6. Bounds: the semi-elasticity factor lies in
   ``[exp(-beta) - 1, exp(beta) - 1]`` for any measured rates.
7. Differential: the log-rate form, which stays the default, equals the
   formula on main before the other forms were added, bit pattern for bit
   pattern.

Two documented behaviors are tested as intended rather than as violations:
below a net-of-tax elasticity of about 0.0027 the 99.9% cap makes revenue at
100% exceed the analytical peak, and a float32 round trip at a large
semi-elasticity loses the multiplier entirely.

Household simulations of these forms are in test_behavioral_response_measurements.py,
which CI runs in the heavy-b group.
"""

from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st
from hypothesis.extra import numpy as hnp

import policyengine_us.variables.gov.simulation.capital_gains_responses as capital_gains_module
from policyengine_us.variables.gov.simulation.capital_gains_response_forms import (
    CAPITAL_GAINS_RESPONSE_FORM_VARIABLES,
    CAPITAL_GAINS_RESPONSE_FORMS,
    CAPITAL_GAINS_RESPONSE_MAXIMUM,
    LOG_RATE_ELASTICITY,
    NET_OF_TAX_ELASTICITY,
    NET_OF_TAX_SHARE_FLOOR,
    SEMI_ELASTICITY,
    capital_gains_response_factor,
    log_rate_elasticity_response_factor,
    net_of_tax_elasticity_response_factor,
    selected_capital_gains_response_form,
    semi_elasticity_response_factor,
)
from policyengine_us.variables.gov.simulation.capital_gains_responses import (
    capital_gains_behavioral_response,
    capital_gains_net_of_tax_elasticity,
    capital_gains_semi_elasticity,
)

# Revenue-maximizing rates of 28.5% to 30% correspond to these semi-elasticities.
CALIBRATED_SEMI_ELASTICITIES = (1 / 0.285, 1 / 0.29, 1 / 0.30)

# Hypothesis input ranges.
RATES = st.floats(min_value=0, max_value=1, allow_nan=False)
WIDE_RATES = st.floats(min_value=-5, max_value=20, allow_nan=False)
LOG_RATE_ELASTICITIES = st.floats(min_value=-3, max_value=0, allow_nan=False)
# The new forms' supported domains.
SEMI_ELASTICITIES = st.floats(
    min_value=0, max_value=CAPITAL_GAINS_RESPONSE_MAXIMUM[SEMI_ELASTICITY]
)
NET_OF_TAX_ELASTICITIES = st.floats(
    min_value=0, max_value=CAPITAL_GAINS_RESPONSE_MAXIMUM[NET_OF_TAX_ELASTICITY]
)
PARAMETERS_BY_FORM = {
    LOG_RATE_ELASTICITY: LOG_RATE_ELASTICITIES,
    SEMI_ELASTICITY: SEMI_ELASTICITIES,
    NET_OF_TAX_ELASTICITY: NET_OF_TAX_ELASTICITIES,
}
FORM_AND_PARAMETER = st.sampled_from(CAPITAL_GAINS_RESPONSE_FORMS).flatmap(
    lambda form: st.tuples(st.just(form), PARAMETERS_BY_FORM[form])
)
# Rates a tax can take over which each form's factor is strictly monotonic.
UNCLIPPED_RATE_RANGE = {
    LOG_RATE_ELASTICITY: (0.001, 1.0),
    SEMI_ELASTICITY: (0.0, 1.0),
    NET_OF_TAX_ELASTICITY: (0.0, 1 - NET_OF_TAX_SHARE_FLOOR),
}
# Allowance for floating-point rounding in revenue comparisons. The multiplier
# 1 + f is computed as 1 + expm1(x), accurate to about 2.2e-16 in absolute
# terms, so where it is near 0 (realizations a trillionth of their baseline or
# less) neighboring rates can round to the same or reversed values. Revenue,
# a rate of at most 1 times the multiplier, is compared to within a relative
# 1e-12 plus an absolute 1e-15.
REVENUE_RTOL = 1e-12
REVENUE_ATOL = 1e-15


def at_most(smaller, larger):
    return smaller <= larger * (1 + REVENUE_RTOL) + REVENUE_ATOL


def main_log_rate_response_factor(baseline_mtr, reform_mtr, elasticity):
    """The response factor on main before this change (75cdd801), kept frozen.

    ``capital_gains_behavioral_response`` computed
    ``np.exp(elasticity * tax_rate_change) - 1`` with the tax rate change from
    ``calculate_relative_capital_gains_mtr_change``, which floored both rates
    at 0.001 and took the difference of their logs.
    """
    min_rate = 0.001
    baseline = np.maximum(baseline_mtr, min_rate)
    reform = np.maximum(reform_mtr, min_rate)
    tax_rate_change = np.log(reform) - np.log(baseline)
    return np.exp(elasticity * tax_rate_change) - 1


def bits(array):
    """An array's bit patterns, so signed zeros and NaN payloads compare too."""
    array = np.asarray(array)
    return array.view(np.uint32 if array.dtype == np.float32 else np.uint64)


def factor(form, baseline_rate, reform_rate, parameter):
    return float(
        capital_gains_response_factor(
            form, np.float64(baseline_rate), np.float64(reform_rate), parameter
        )
    )


def revenue(form, baseline_rate, rate, parameter):
    return rate * (1 + factor(form, baseline_rate, rate, parameter))


def capital_gains_responses(**values):
    defaults = {form: 0.0 for form in CAPITAL_GAINS_RESPONSE_FORMS}
    return SimpleNamespace(**{**defaults, **values})


def make_parameters(**values):
    return lambda period: SimpleNamespace(
        gov=SimpleNamespace(
            simulation=SimpleNamespace(
                capital_gains_responses=capital_gains_responses(**values)
            )
        )
    )


class FakePerson:
    def __init__(self, values):
        self.simulation = SimpleNamespace(baseline=object())
        self.values = values

    def __call__(self, variable, period, options=None):
        return self.values[variable]


# Known values for each form.


def test_log_rate_form_matches_hand_calculation():
    # Doubling the rate at an elasticity of -1 halves realizations.
    assert factor(LOG_RATE_ELASTICITY, 0.2, 0.4, -1.0) == pytest.approx(-0.5)
    # (0.25 / 0.20) ** -0.7 - 1
    assert factor(LOG_RATE_ELASTICITY, 0.2, 0.25, -0.7) == pytest.approx(1.25**-0.7 - 1)


def test_log_rate_form_floors_a_zero_baseline_rate_at_one_tenth_of_a_percent():
    # A move from 0% to 15% is a log change of ln(0.15 / 0.001) = ln(150),
    # about 5.0, which at an elasticity of -0.7 removes about 97% of gains.
    assert np.log(0.15 / 0.001) == pytest.approx(5.01, abs=0.01)
    assert factor(LOG_RATE_ELASTICITY, 0.0, 0.15, -0.7) == pytest.approx(150**-0.7 - 1)
    assert factor(LOG_RATE_ELASTICITY, 0.0, 0.15, -0.7) == pytest.approx(
        -0.970, abs=0.001
    )
    # The floor also applies to negative measured rates, and there is no cap.
    assert factor(LOG_RATE_ELASTICITY, -0.3, 0.15, -0.7) == factor(
        LOG_RATE_ELASTICITY, 0.0, 0.15, -0.7
    )
    assert factor(LOG_RATE_ELASTICITY, 0.2, 3.0, -0.7) == pytest.approx(15**-0.7 - 1)


def test_semi_elasticity_form_matches_hand_calculation():
    assert factor(SEMI_ELASTICITY, 0.2, 0.3, 3.4) == pytest.approx(np.exp(-0.34) - 1)
    assert factor(SEMI_ELASTICITY, 0.3, 0.2, 3.4) == pytest.approx(np.exp(0.34) - 1)


def test_semi_elasticity_form_is_well_defined_at_a_zero_baseline_rate():
    # Only the change in the rate matters, so a 0% baseline needs no floor:
    # a move from 0% to 15% at beta = 3.4 removes 1 - exp(-0.51), about 40%,
    # where the log-rate form at -0.7 removes about 97%.
    assert factor(SEMI_ELASTICITY, 0.0, 0.15, 3.4) == pytest.approx(np.exp(-0.51) - 1)
    assert factor(SEMI_ELASTICITY, 0.0, 0.15, 3.4) == pytest.approx(-0.40, abs=0.001)
    assert factor(SEMI_ELASTICITY, 0.0, 0.15, 3.4) == factor(
        SEMI_ELASTICITY, 0.10, 0.25, 3.4
    )


def test_semi_elasticity_form_clips_rates_to_zero_and_one():
    # A benefit cliff can put the household finite-difference rate above 1.
    assert factor(SEMI_ELASTICITY, 3.0, 0.25, 3.4) == pytest.approx(
        np.exp(3.4 * 0.75) - 1
    )
    assert factor(SEMI_ELASTICITY, -0.4, 0.25, 3.4) == pytest.approx(
        np.exp(-3.4 * 0.25) - 1
    )
    assert factor(SEMI_ELASTICITY, 3.0, 5.0, 3.4) == 0


def test_net_of_tax_form_matches_hand_calculation():
    # ((1 - 0.4) / (1 - 0.2)) ** 0.5 - 1
    assert factor(NET_OF_TAX_ELASTICITY, 0.2, 0.4, 0.5) == pytest.approx(0.75**0.5 - 1)
    assert factor(NET_OF_TAX_ELASTICITY, 0.0, 0.1, 0.7) == pytest.approx(0.9**0.7 - 1)


def test_net_of_tax_form_floors_the_net_of_tax_share():
    # Rates at or above 99.9% are treated as 99.9%.
    assert factor(NET_OF_TAX_ELASTICITY, 1.0, 0.5, 0.5) == pytest.approx(
        (0.5 / NET_OF_TAX_SHARE_FLOOR) ** 0.5 - 1
    )
    assert factor(NET_OF_TAX_ELASTICITY, 4.0, 0.5, 0.5) == factor(
        NET_OF_TAX_ELASTICITY, 0.999, 0.5, 0.5
    )


def test_calibrated_semi_elasticities_put_the_revenue_peak_at_28_5_to_30_percent():
    grid = np.linspace(0, 1, 100_001)
    for semi_elasticity, peak in zip(CALIBRATED_SEMI_ELASTICITIES, (0.285, 0.29, 0.30)):
        revenues = grid * (
            1 + semi_elasticity_response_factor(0.238, grid, semi_elasticity)
        )
        assert grid[np.argmax(revenues)] == pytest.approx(peak, abs=1e-5)
    assert CALIBRATED_SEMI_ELASTICITIES[0] == pytest.approx(3.509, abs=0.001)
    assert CALIBRATED_SEMI_ELASTICITIES[-1] == pytest.approx(3.333, abs=0.001)


def test_vectorized_factors_match_scalar_factors():
    baseline = np.array([0.0, 0.15, 0.238, 0.5, 1.2], dtype=np.float32)
    reform = np.array([0.1, 0.25, 0.338, 0.4, 0.3], dtype=np.float32)
    for form, parameter in (
        (LOG_RATE_ELASTICITY, -0.7),
        (SEMI_ELASTICITY, 3.4),
        (NET_OF_TAX_ELASTICITY, 0.7),
    ):
        vectorized = capital_gains_response_factor(form, baseline, reform, parameter)
        assert vectorized.shape == baseline.shape
        for i in range(len(baseline)):
            assert vectorized[i] == pytest.approx(
                factor(form, baseline[i], reform[i], parameter), rel=1e-5
            )


# Selecting the form.


def test_no_form_is_selected_when_every_parameter_is_zero():
    assert selected_capital_gains_response_form(capital_gains_responses()) is None


@pytest.mark.parametrize("form", CAPITAL_GAINS_RESPONSE_FORMS)
def test_the_nonzero_parameter_selects_its_form(form):
    responses = capital_gains_responses(**{form: 0.5})
    assert selected_capital_gains_response_form(responses) == form


@pytest.mark.parametrize(
    "values",
    [
        {"elasticity": -0.7, "semi_elasticity": 3.4},
        {"elasticity": -0.7, "net_of_tax_elasticity": 0.7},
        {"semi_elasticity": 3.4, "net_of_tax_elasticity": 0.7},
        {"elasticity": -0.7, "semi_elasticity": 3.4, "net_of_tax_elasticity": 0.7},
    ],
)
def test_more_than_one_nonzero_parameter_is_an_error(values):
    with pytest.raises(ValueError, match="at most one"):
        selected_capital_gains_response_form(capital_gains_responses(**values))


@pytest.mark.parametrize(
    "form, value",
    [
        # A semi-elasticity entered with the log-rate elasticity's sign.
        (SEMI_ELASTICITY, -3.4),
        (SEMI_ELASTICITY, 50.5),
        (NET_OF_TAX_ELASTICITY, -0.7),
        (NET_OF_TAX_ELASTICITY, 5.5),
    ],
)
def test_new_forms_reject_parameters_outside_their_domain(form, value):
    with pytest.raises(ValueError, match="must be between 0 and"):
        selected_capital_gains_response_form(capital_gains_responses(**{form: value}))


@pytest.mark.parametrize("form", CAPITAL_GAINS_RESPONSE_FORMS)
@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_every_form_rejects_a_parameter_that_is_not_finite(form, value):
    with pytest.raises(ValueError, match="must be finite"):
        selected_capital_gains_response_form(capital_gains_responses(**{form: value}))


@pytest.mark.parametrize("value", [-5.0, -0.7, 0.5])
def test_log_rate_form_accepts_any_finite_elasticity(value):
    responses = capital_gains_responses(elasticity=value)
    assert selected_capital_gains_response_form(responses) == LOG_RATE_ELASTICITY


@pytest.mark.parametrize("form", [SEMI_ELASTICITY, NET_OF_TAX_ELASTICITY])
def test_new_forms_accept_their_maximum(form):
    maximum = CAPITAL_GAINS_RESPONSE_MAXIMUM[form]
    responses = capital_gains_responses(**{form: maximum})
    assert selected_capital_gains_response_form(responses) == form


def test_defaults_select_no_response_in_every_year():
    from policyengine_us.system import system

    parameters = system.parameters
    for year in range(2000, 2101, 5):
        responses = parameters(f"{year}-01-01").gov.simulation.capital_gains_responses
        assert responses.elasticity == 0
        assert responses.semi_elasticity == 0
        assert responses.net_of_tax_elasticity == 0
        assert selected_capital_gains_response_form(responses) is None


# The behavioral response variable.


MEASUREMENTS = {
    "baseline_capital_gains_mtr": np.array([0.0, 0.2, 0.238], dtype=np.float32),
    "reform_capital_gains_mtr": np.array([0.1, 0.3, 0.198], dtype=np.float32),
}
GAINS = np.array([100.0, 200.0, -50.0], dtype=np.float32)


def response_with(monkeypatch, measurements=MEASUREMENTS, **values):
    monkeypatch.setattr(
        capital_gains_module,
        "get_behavioral_response_measurements",
        lambda person, period: measurements,
    )
    person = FakePerson(
        {
            "long_term_capital_gains_before_response": GAINS,
            **{
                CAPITAL_GAINS_RESPONSE_FORM_VARIABLES[form]: np.full(
                    3, value, dtype=np.float32
                )
                for form, value in values.items()
            },
        }
    )
    return capital_gains_behavioral_response.formula(
        person, 2026, make_parameters(**values)
    )


def test_response_uses_the_semi_elasticity_form(monkeypatch):
    response = response_with(monkeypatch, semi_elasticity=3.4)
    change = (
        MEASUREMENTS["reform_capital_gains_mtr"]
        - MEASUREMENTS["baseline_capital_gains_mtr"]
    )
    assert np.allclose(response, GAINS * np.expm1(-3.4 * change), rtol=1e-6)
    # The first two rates rise, so their gains fall. The third rate falls, so
    # that person's realizations grow, which makes their net loss larger.
    assert response[0] < 0 and response[1] < 0 and response[2] < 0


def test_response_uses_the_net_of_tax_form(monkeypatch):
    response = response_with(monkeypatch, net_of_tax_elasticity=0.5)
    baseline_share = 1 - MEASUREMENTS["baseline_capital_gains_mtr"]
    reform_share = 1 - MEASUREMENTS["reform_capital_gains_mtr"]
    assert np.allclose(
        response, GAINS * ((reform_share / baseline_share) ** 0.5 - 1), rtol=1e-5
    )


def test_default_log_rate_response_matches_main_bit_for_bit(monkeypatch):
    response = response_with(monkeypatch, elasticity=-0.7)
    elasticity = np.full(3, -0.7, dtype=np.float32)
    expected = GAINS * main_log_rate_response_factor(
        MEASUREMENTS["baseline_capital_gains_mtr"],
        MEASUREMENTS["reform_capital_gains_mtr"],
        elasticity,
    )
    assert response.dtype == expected.dtype
    assert np.array_equal(bits(response), bits(expected))


def test_response_rejects_person_level_parameters_outside_the_domain(monkeypatch):
    monkeypatch.setattr(
        capital_gains_module,
        "get_behavioral_response_measurements",
        lambda person, period: MEASUREMENTS,
    )
    person = FakePerson(
        {
            "long_term_capital_gains_before_response": GAINS,
            "capital_gains_semi_elasticity": np.array(
                [3.4, -3.4, 3.4], dtype=np.float32
            ),
        }
    )
    with pytest.raises(ValueError, match="must be between 0 and 50"):
        capital_gains_behavioral_response.formula(
            person, 2026, make_parameters(semi_elasticity=3.4)
        )


@pytest.mark.parametrize(
    "values", [{"semi_elasticity": 3.4}, {"net_of_tax_elasticity": 0.7}]
)
def test_new_forms_raise_on_a_rate_that_is_not_finite(monkeypatch, values):
    measurements = {
        "baseline_capital_gains_mtr": np.array([0.2, np.nan, 0.2], dtype=np.float32),
        "reform_capital_gains_mtr": np.array([0.3, 0.3, 0.3], dtype=np.float32),
    }
    with pytest.raises(ValueError, match="not finite for 1 people"):
        response_with(monkeypatch, measurements, **values)


def test_log_rate_form_still_passes_a_rate_that_is_not_finite_through(monkeypatch):
    """The default path is unchanged, including its silence on a NaN rate."""
    measurements = {
        "baseline_capital_gains_mtr": np.array([0.2, np.nan, 0.2], dtype=np.float32),
        "reform_capital_gains_mtr": np.array([0.3, 0.3, 0.3], dtype=np.float32),
    }
    response = response_with(monkeypatch, measurements, elasticity=-0.7)
    assert np.isnan(response[1]) and np.isfinite(response[[0, 2]]).all()


def test_response_is_zero_without_measuring_when_no_form_is_selected(monkeypatch):
    def fail(person, period):
        raise AssertionError("measured although no response form is selected")

    monkeypatch.setattr(
        capital_gains_module, "get_behavioral_response_measurements", fail
    )
    person = FakePerson({})
    assert (
        capital_gains_behavioral_response.formula(person, 2026, make_parameters()) == 0
    )


def test_response_raises_when_two_forms_are_selected(monkeypatch):
    with pytest.raises(ValueError, match="at most one"):
        response_with(monkeypatch, elasticity=-0.7, semi_elasticity=3.4)


def test_response_is_zero_without_a_baseline():
    person = FakePerson({})
    person.simulation.baseline = None
    parameters = make_parameters(semi_elasticity=3.4)
    assert capital_gains_behavioral_response.formula(person, 2026, parameters) == 0


def test_form_parameter_variables_read_their_parameters():
    parameters = make_parameters(semi_elasticity=3.4, net_of_tax_elasticity=0.7)
    person = FakePerson({})
    assert capital_gains_semi_elasticity.formula(person, 2026, parameters) == 3.4
    assert capital_gains_net_of_tax_elasticity.formula(person, 2026, parameters) == 0.7


# Properties.


@given(form_and_parameter=FORM_AND_PARAMETER, rate=WIDE_RATES)
def test_no_rate_change_means_no_response(form_and_parameter, rate):
    form, parameter = form_and_parameter
    assert factor(form, rate, rate, parameter) == 0


@given(
    form_and_parameter=FORM_AND_PARAMETER,
    baseline=WIDE_RATES,
    low=WIDE_RATES,
    high=WIDE_RATES,
)
def test_realizations_do_not_rise_with_the_rate(
    form_and_parameter, baseline, low, high
):
    form, parameter = form_and_parameter
    low, high = sorted((low, high))
    assert factor(form, baseline, low, parameter) >= factor(
        form, baseline, high, parameter
    )
    # Equivalently, realizations do not fall as the baseline rate rises.
    assert factor(form, low, baseline, parameter) <= factor(
        form, high, baseline, parameter
    )


@given(
    form=st.sampled_from(CAPITAL_GAINS_RESPONSE_FORMS),
    magnitude=st.floats(min_value=0.05, max_value=5),
    baseline=RATES,
    low=st.floats(min_value=0, max_value=1),
    gap=st.floats(min_value=1e-4, max_value=1),
)
def test_realizations_fall_strictly_inside_the_unclipped_range(
    form, magnitude, baseline, low, gap
):
    lower_bound, upper_bound = UNCLIPPED_RATE_RANGE[form]
    low = lower_bound + low * (upper_bound - lower_bound)
    high = low + gap
    assume(high <= upper_bound)
    parameter = -magnitude if form == LOG_RATE_ELASTICITY else magnitude
    at_low = factor(form, baseline, low, parameter)
    at_high = factor(form, baseline, high, parameter)
    # Near f = -1 a small rate step moves 1 + f by less than f's rounding.
    assume(1 + at_high > 1e-6)
    assert at_low > at_high


@given(
    form_and_parameter=FORM_AND_PARAMETER,
    baseline=WIDE_RATES,
    reform=WIDE_RATES,
    gains=st.floats(min_value=-1e10, max_value=1e10),
)
def test_response_never_flips_the_sign_of_gains(
    form_and_parameter, baseline, reform, gains
):
    form, parameter = form_and_parameter
    change = factor(form, baseline, reform, parameter)
    assert 1 + change >= 0
    assert gains * (1 + change) * np.sign(gains) >= 0


@given(
    form_and_parameter=FORM_AND_PARAMETER,
    first=WIDE_RATES,
    second=WIDE_RATES,
    third=WIDE_RATES,
)
def test_response_factors_compose_along_a_path_of_rates(
    form_and_parameter, first, second, third
):
    form, parameter = form_and_parameter
    legs = (
        1 + factor(form, first, second, parameter),
        1 + factor(form, second, third, parameter),
    )
    direct = 1 + factor(form, first, third, parameter)
    # 1 + f is accurate to about 1e-16 in absolute terms, so when it is tiny a
    # large second leg magnifies that error; keep factors that carry at least
    # ten significant digits.
    assume(min(*legs, direct) > 1e-6)
    assert legs[0] * legs[1] == pytest.approx(direct, rel=1e-9)


@given(semi_elasticity=SEMI_ELASTICITIES, baseline=WIDE_RATES, reform=WIDE_RATES)
def test_semi_elasticity_factor_is_bounded(semi_elasticity, baseline, reform):
    change = factor(SEMI_ELASTICITY, baseline, reform, semi_elasticity)
    assert np.expm1(-semi_elasticity) <= change <= np.expm1(semi_elasticity)


@given(
    semi_elasticity=st.floats(min_value=1.05, max_value=50),
    baseline=RATES,
    rate=RATES,
    other_rate=RATES,
)
# Multipliers near 0 that rounding leaves flat or reversed (review of #10054).
@example(semi_elasticity=50, baseline=0, rate=0.6305, other_rate=0.6306)
def test_semi_elasticity_revenue_peaks_at_the_inverse_semi_elasticity(
    semi_elasticity, baseline, rate, other_rate
):
    peak = 1 / semi_elasticity
    peak_revenue = revenue(SEMI_ELASTICITY, baseline, peak, semi_elasticity)
    assert peak_revenue > 0
    assert at_most(
        revenue(SEMI_ELASTICITY, baseline, rate, semi_elasticity), peak_revenue
    )
    # Unimodal: rising below the peak and falling above it.
    low, high = sorted((rate, other_rate))
    low_revenue = revenue(SEMI_ELASTICITY, baseline, low, semi_elasticity)
    high_revenue = revenue(SEMI_ELASTICITY, baseline, high, semi_elasticity)
    if high <= peak:
        assert at_most(low_revenue, high_revenue)
    if low >= peak:
        assert at_most(high_revenue, low_revenue)


@given(
    net_of_tax_elasticity=st.floats(min_value=0.003, max_value=20),
    baseline=st.floats(min_value=0, max_value=0.99),
    rate=RATES,
    other_rate=RATES,
)
@example(net_of_tax_elasticity=20, baseline=0, rate=0.8, other_rate=0.8001)
def test_net_of_tax_revenue_peaks_at_one_over_one_plus_the_elasticity(
    net_of_tax_elasticity, baseline, rate, other_rate
):
    peak = 1 / (1 + net_of_tax_elasticity)
    peak_revenue = revenue(NET_OF_TAX_ELASTICITY, baseline, peak, net_of_tax_elasticity)
    assert at_most(
        revenue(NET_OF_TAX_ELASTICITY, baseline, rate, net_of_tax_elasticity),
        peak_revenue,
    )
    low, high = sorted((rate, other_rate))
    low_revenue = revenue(NET_OF_TAX_ELASTICITY, baseline, low, net_of_tax_elasticity)
    high_revenue = revenue(NET_OF_TAX_ELASTICITY, baseline, high, net_of_tax_elasticity)
    if high <= peak:
        assert at_most(low_revenue, high_revenue)
    # Above the 99.9% cap realizations stop falling and revenue rises again.
    if peak <= low and high <= 1 - NET_OF_TAX_SHARE_FLOOR:
        assert at_most(high_revenue, low_revenue)


def test_net_of_tax_cap_puts_revenue_at_100_percent_above_a_tiny_elasticitys_peak():
    """Intended: below an elasticity of about 0.0027 the cap moves the maximum.

    At 0.002 the analytical peak is a 99.8% rate, and revenue at 100%, where
    the cap holds realizations at their 99.9% level, is higher. At 0.003 the
    analytical peak is higher.
    """
    for elasticity, cap_wins in ((0.002, True), (0.003, False)):
        peak = 1 / (1 + elasticity)
        at_peak = revenue(NET_OF_TAX_ELASTICITY, 0.0, peak, elasticity)
        at_100 = revenue(NET_OF_TAX_ELASTICITY, 0.0, 1.0, elasticity)
        assert (at_100 > at_peak) is cap_wins


@given(
    elasticity=st.floats(min_value=-0.99, max_value=0),
    baseline=RATES,
    rate=st.floats(min_value=0.001, max_value=1),
    other_rate=st.floats(min_value=0.001, max_value=1),
)
def test_log_rate_revenue_has_no_interior_peak_above_minus_one(
    elasticity, baseline, rate, other_rate
):
    """The problem the semi-elasticity form solves: revenue keeps rising."""
    low, high = sorted((rate, other_rate))
    assert at_most(
        revenue(LOG_RATE_ELASTICITY, baseline, low, elasticity),
        revenue(LOG_RATE_ELASTICITY, baseline, high, elasticity),
    )


# No deadline: a wall-clock limit is not part of this compatibility property,
# and generating float32 arrays can exceed Hypothesis's 200 ms default on a
# loaded runner (it did once in review, 253 ms, then 86 ms on replay).
@settings(max_examples=300, deadline=None)
@given(
    dtype=st.sampled_from([np.float32, np.float64]),
    data=st.data(),
)
def test_log_rate_form_matches_main_bit_for_bit(dtype, data):
    shape = data.draw(st.integers(min_value=1, max_value=20))
    rate_elements = st.floats(
        min_value=-2,
        max_value=5,
        allow_nan=False,
        width=32 if dtype is np.float32 else 64,
    )
    baseline = data.draw(hnp.arrays(dtype, shape, elements=rate_elements))
    reform = data.draw(hnp.arrays(dtype, shape, elements=rate_elements))
    elasticity = data.draw(
        hnp.arrays(
            dtype,
            shape,
            elements=st.floats(
                min_value=-3,
                max_value=0,
                allow_nan=False,
                width=32 if dtype is np.float32 else 64,
            ),
        )
    )
    new = log_rate_elasticity_response_factor(baseline, reform, elasticity)
    old = main_log_rate_response_factor(baseline, reform, elasticity)
    assert new.dtype == old.dtype
    assert np.array_equal(bits(new), bits(old))


FLOAT32_RATES = st.floats(min_value=-5, max_value=20, width=32)
# 2 ** 53, about $9 quadrillion, is exact in float32 and inside the documented
# $10 quadrillion limit.
FLOAT32_GAINS = st.floats(min_value=-(2.0**53), max_value=2.0**53, width=32)


@settings(deadline=None)
@given(
    form=st.sampled_from([SEMI_ELASTICITY, NET_OF_TAX_ELASTICITY]),
    data=st.data(),
)
def test_new_forms_give_finite_sign_preserving_float32_responses(form, data):
    """Across each new form's domain, as the model computes it in float32."""
    size = data.draw(st.integers(min_value=1, max_value=20))
    parameter = data.draw(
        hnp.arrays(
            np.float32,
            size,
            elements=st.floats(
                min_value=0,
                max_value=CAPITAL_GAINS_RESPONSE_MAXIMUM[form],
                width=32,
            ),
        )
    )
    baseline = data.draw(hnp.arrays(np.float32, size, elements=FLOAT32_RATES))
    reform = data.draw(hnp.arrays(np.float32, size, elements=FLOAT32_RATES))
    gains = data.draw(hnp.arrays(np.float32, size, elements=FLOAT32_GAINS))
    response = gains * capital_gains_response_factor(form, baseline, reform, parameter)
    assert response.dtype == np.float32
    assert np.isfinite(response).all()
    after = gains + response
    assert (after * np.sign(gains) >= 0).all()


@pytest.mark.parametrize(
    "dtype, semi_elasticity, round_trip",
    [
        (np.float32, 3.4, 1.000001),
        # Intended: exp(-20) is stored as a multiplier with no significant
        # digits left once 1 is added back, so the return leg cannot undo it.
        (np.float32, 20, 0.0),
        (np.float64, 20, 1.0),
    ],
)
def test_round_trip_precision_matches_the_documentation(
    dtype, semi_elasticity, round_trip
):
    zero, one, beta = dtype(0), dtype(1), dtype(semi_elasticity)
    out = 1 + semi_elasticity_response_factor(zero, one, beta)
    back = 1 + semi_elasticity_response_factor(one, zero, beta)
    assert out * back == pytest.approx(round_trip, rel=1e-6, abs=1e-12)
