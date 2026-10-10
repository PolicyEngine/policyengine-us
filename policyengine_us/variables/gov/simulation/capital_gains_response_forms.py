"""Functional forms for the capital gains realization response.

Each form maps a person's baseline and reform marginal tax rates on capital
gains (``tau0`` and ``tau1``) to a response factor ``f``. The behavioral
response is ``long_term_capital_gains_before_response * f``, so realizations
after the response are the pre-response gains times ``1 + f``. Every form has
``1 + f >= 0``, so the response never changes the sign of a person's gains, and
``f = 0`` when ``tau1 == tau0``.

The form is chosen by which of three parameters under
``gov.simulation.capital_gains_responses`` is nonzero:

- ``elasticity`` (log-rate form, the original):
  ``1 + f = exp(elasticity * [ln tau1 - ln tau0])``, with both rates floored
  at 0.001 by ``calculate_relative_capital_gains_mtr_change``. Revenue
  ``tau * R`` is proportional to ``tau ** (1 + elasticity)``, so for an
  elasticity above -1 it rises all the way to a 100% rate and the form has no
  interior revenue-maximizing rate. Because of the floor, a person whose
  baseline rate is 0% gets a log change of ``ln(tau1 / 0.001)``: about 5.0 for
  a move to 15%, which removes about 97% of their realizations at an
  elasticity of -0.7.
- ``semi_elasticity``: ``1 + f = exp(-semi_elasticity * (tau1 - tau0))``, with
  both rates clipped to [0, 1]. It is defined at ``tau0 = 0`` with no floor.
  Revenue ``tau * R`` peaks at ``tau = 1 / semi_elasticity``.
- ``net_of_tax_elasticity``:
  ``1 + f = exp(net_of_tax_elasticity * [ln(1 - tau1) - ln(1 - tau0)])``, with
  both rates clipped to [0, 1 - NET_OF_TAX_SHARE_FLOOR]. Revenue peaks at
  ``tau = 1 / (1 + net_of_tax_elasticity)``. The floor on the net-of-tax share
  mirrors the log-rate form's floor on the rate: a baseline rate at or above
  99.9% gives a large log change for any reform rate below it.

The rates are household finite-difference marginal rates
(``marginal_tax_rate_on_capital_gains``), which can fall outside [0, 1] when an
extra $1,000 of gains crosses a benefit cliff or phase-in. The semi-elasticity
and net-of-tax forms clip them to the range a tax rate can take, which bounds
the semi-elasticity factor to [exp(-semi_elasticity), exp(semi_elasticity)].
The log-rate form keeps its original floor and no cap, so scores that use it do
not change.
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


def selected_capital_gains_response_form(capital_gains_responses):
    """The form whose parameter is nonzero, or None when all are zero.

    Raises ValueError when more than one is nonzero: the forms are
    alternatives, and combining them would apply the response more than once.
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
    return next(iter(nonzero))


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
