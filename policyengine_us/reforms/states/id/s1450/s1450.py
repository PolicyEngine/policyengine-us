from policyengine_core.periods import instant
from policyengine_core.periods import period as period_
from policyengine_core.reforms import Reform

from policyengine_us.model_api import *


def create_id_s1450() -> Reform:
    def modify_parameters(parameters: ParameterNode) -> ParameterNode:
        # Restore id_ctc to the non-refundable credits list for 2026+
        # The baseline has 2026-01-01: [] which removes it
        parameters.gov.states.id.tax.income.credits.non_refundable.update(
            start=instant("2026-01-01"),
            stop=instant("2100-12-31"),
            value=["id_ctc"],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def create_id_s1450_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_id_s1450()

    p = parameters.gov.contrib.states.id.s1450

    # 5-year lookahead
    reform_active = False
    current_period = period_(period)

    for i in range(5):
        p_at_period = p(current_period)
        if p_at_period.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_id_s1450()
    else:
        return None


id_s1450 = create_id_s1450_reform(None, None, bypass=True)
