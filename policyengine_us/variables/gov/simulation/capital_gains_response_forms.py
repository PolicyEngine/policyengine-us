"""Functional forms for the capital gains realization response.

Each form maps a person's baseline and reform marginal tax rates on capital
gains (``tau0`` and ``tau1``) to a response factor ``f``. The behavioral
response is ``long_term_capital_gains_before_response * f``, so realizations
after the response are the pre-response gains times the multiplier ``1 + f``.
Every form has ``1 + f >= 0``, so the response never changes the sign of a
person's gains, and ``f = 0`` when ``tau1 == tau0``. For a net loss the
multiplier scales the loss, so a smaller multiplier moves it toward zero.

The form is chosen by which of three parameters under
``gov.simulation.capital_gains_responses`` is nonzero:

- ``elasticity`` (log-rate form, the original):
  ``1 + f = exp(elasticity * [ln tau1 - ln tau0])``, with both rates floored
  at 0.001 by ``calculate_relative_capital_gains_mtr_change``. In a single-rate
  model, revenue ``tau * R`` is proportional to ``tau ** (1 + elasticity)``, so
  for an elasticity between -1 and 0 it rises all the way to a 100% rate and
  the form has no interior revenue-maximizing rate. Because of the floor, a
  person whose baseline rate is 0% gets a log change of ``ln(tau1 / 0.001)``:
  about 5.0 for a move to 15%, which removes about 97% of their realizations
  at an elasticity of -0.7.
- ``semi_elasticity``: ``1 + f = exp(-semi_elasticity * (tau1 - tau0))``, with
  both rates clipped to [0, 1]. It is defined at ``tau0 = 0`` with no floor.
  In a single-rate model, revenue ``tau * R`` peaks at
  ``tau = 1 / semi_elasticity`` when that is below 1 (a semi-elasticity above
  1); otherwise it rises to a 100% rate.
- ``net_of_tax_elasticity``:
  ``1 + f = exp(net_of_tax_elasticity * [ln(1 - tau1) - ln(1 - tau0)])``, with
  both rates clipped to [0, 1 - NET_OF_TAX_SHARE_FLOOR]. In a single-rate
  model, revenue peaks at ``tau = 1 / (1 + net_of_tax_elasticity)`` for a
  net-of-tax elasticity of at least 0.003. Above the 99.9% cap realizations
  stop falling, so revenue rises again at the very top, and for elasticities
  below about 0.0027, whose analytical peak is above 99.7%, revenue at 100%
  is higher.
  The floor on the net-of-tax share mirrors the log-rate form's floor on the
  rate: a baseline rate at or above 99.9% gives a large log change for a
  reform rate well below 99.9%.

A progressive tax schedule, other taxes and benefit interactions move the
model's revenue-maximizing statutory rate away from these single-rate peaks.

The rates are household finite-difference marginal rates
(``marginal_tax_rate_on_capital_gains``), which can fall outside [0, 1] when the
extra gain crosses a benefit cliff or phase-in. The semi-elasticity and
net-of-tax forms clip them to the range a tax rate can take, which bounds the
semi-elasticity multiplier ``1 + f`` to
[exp(-semi_elasticity), exp(semi_elasticity)].

The new forms accept only positive parameters, the sign under which
realizations fall as the rate rises, up to the maxima below; zero leaves the
form unselected. That rejects the likeliest slip, entering a semi-elasticity
with the negative sign the log-rate elasticity uses. The log-rate form keeps
its original arithmetic and accepts any finite elasticity, so scores that use
it do not change.
"""

import numpy as np

from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    calculate_relative_capital_gains_mtr_change,
)

LOG_RATE_ELASTICITY = "elasticity"
SEMI_ELASTICITY = "semi_elasticity"
NET_OF_TAX_ELASTICITY = "net_of_tax_elasticity"
CAPITAL_GAINS_RESPONSE_FORMS = (
    LOG_RATE_ELASTICITY,
    SEMI_ELASTICITY,
    NET_OF_TAX_ELASTICITY,
)
# The person-level variable that carries each form's parameter.
CAPITAL_GAINS_RESPONSE_FORM_VARIABLES = {
    LOG_RATE_ELASTICITY: "capital_gains_elasticity",
    SEMI_ELASTICITY: "capital_gains_semi_elasticity",
    NET_OF_TAX_ELASTICITY: "capital_gains_net_of_tax_elasticity",
}
NET_OF_TAX_SHARE_FLOOR = 0.001
# Largest parameter each new form accepts. At these limits the multiplier
# 1 + f is at most exp(50), about 5.2e21 (a semi-elasticity of 50 and a rate
# falling from 100% to 0%), or 1000 ** 5 = 1e15 (a net-of-tax elasticity of 5
# and a net-of-tax share rising from 0.001 to 1), so the response to gains
# below $10 quadrillion stays finite in float32. The semi-elasticities in CRS
# R41364's Table 1 run from 1.0 to 4.1.
CAPITAL_GAINS_RESPONSE_MAXIMUM = {
    SEMI_ELASTICITY: 50,
    NET_OF_TAX_ELASTICITY: 5,
}


def check_capital_gains_response_parameter(form, values):
    """Raise ValueError unless ``values`` are in the form's supported domain.

    Every form needs finite values. The semi-elasticity and net-of-tax forms
    also need values from 0 to their maximum, 0 meaning no response.
    """
    values = np.asarray(values, dtype=np.float64)
    name = f"gov.simulation.capital_gains_responses.{form}"
    if not np.all(np.isfinite(values)):
        raise ValueError(f"{name} must be finite; got {values[~np.isfinite(values)]}.")
    if form not in CAPITAL_GAINS_RESPONSE_MAXIMUM:
        return
    maximum = CAPITAL_GAINS_RESPONSE_MAXIMUM[form]
    outside = (values < 0) | (values > maximum)
    if np.any(outside):
        raise ValueError(
            f"{name} must be between 0 and {maximum}; got {values[outside]}. It is "
            "positive when realizations fall as the rate rises, unlike the "
            "negative log-rate elasticity: a semi-elasticity of 3.4 cuts "
            "realizations by about 3.4% per percentage point."
        )


def selected_capital_gains_response_form(capital_gains_responses):
    """The form whose parameter is nonzero, or None when all are zero.

    Raises ValueError when more than one is nonzero, because the forms are
    alternatives and combining them would apply the response more than once,
    and when the selected parameter is outside its supported domain.
    """
    values = {
        form: getattr(capital_gains_responses, form)
        for form in CAPITAL_GAINS_RESPONSE_FORMS
    }
    nonzero = {form: value for form, value in values.items() if value != 0}
    if len(nonzero) > 1:
        settings = ", ".join(f"{form}={value}" for form, value in nonzero.items())
        raise ValueError(
            "Set at most one of gov.simulation.capital_gains_responses."
            f"{{{', '.join(CAPITAL_GAINS_RESPONSE_FORMS)}}} to a nonzero value; "
            f"got {settings}. Each selects a different functional form for the "
            "capital gains realization response."
        )
    if not nonzero:
        return None
    form, value = next(iter(nonzero.items()))
    check_capital_gains_response_parameter(form, value)
    return form


def log_rate_elasticity_response_factor(baseline_rate, reform_rate, elasticity):
    """Response factor for realizations proportional to rate ** elasticity."""
    log_rate_change = calculate_relative_capital_gains_mtr_change(
        {
            "baseline_capital_gains_mtr": baseline_rate,
            "reform_capital_gains_mtr": reform_rate,
        }
    )
    return np.exp(elasticity * log_rate_change) - 1


def semi_elasticity_response_factor(baseline_rate, reform_rate, semi_elasticity):
    """Response factor for realizations proportional to exp(-semi_elasticity * rate)."""
    baseline = np.clip(baseline_rate, 0, 1)
    reform = np.clip(reform_rate, 0, 1)
    return np.expm1(-semi_elasticity * (reform - baseline))


def net_of_tax_elasticity_response_factor(baseline_rate, reform_rate, elasticity):
    """Response factor for realizations proportional to (1 - rate) ** elasticity."""
    max_rate = 1 - NET_OF_TAX_SHARE_FLOOR
    baseline_share = 1 - np.clip(baseline_rate, 0, max_rate)
    reform_share = 1 - np.clip(reform_rate, 0, max_rate)
    return np.expm1(elasticity * (np.log(reform_share) - np.log(baseline_share)))


CAPITAL_GAINS_RESPONSE_FACTORS = {
    LOG_RATE_ELASTICITY: log_rate_elasticity_response_factor,
    SEMI_ELASTICITY: semi_elasticity_response_factor,
    NET_OF_TAX_ELASTICITY: net_of_tax_elasticity_response_factor,
}


def capital_gains_response_factor(form, baseline_rate, reform_rate, parameter):
    return CAPITAL_GAINS_RESPONSE_FACTORS[form](baseline_rate, reform_rate, parameter)


def check_capital_gains_response_is_finite(form, response):
    """Raise ValueError if a new form's response is NaN or infinite.

    With parameters in their supported domain this happens only when a measured
    rate or a person's gains is not finite, or gains exceed $10 quadrillion.
    The log-rate form is left unchecked, as it was before the other forms were
    added.
    """
    if form == LOG_RATE_ELASTICITY:
        return
    finite = np.isfinite(response)
    if not np.all(finite):
        raise ValueError(
            f"The {form} capital gains response is not finite for "
            f"{np.count_nonzero(~finite)} people; check their measured "
            "marginal_tax_rate_on_capital_gains and pre-response gains."
        )
