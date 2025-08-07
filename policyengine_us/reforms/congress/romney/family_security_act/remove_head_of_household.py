from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_remove_head_of_household() -> Reform:
    class reform(Reform):
        def apply(self):
            self.neutralize_variable("head_of_household_eligible")

    return reform


def create_remove_head_of_household_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_remove_head_of_household()

    # Look ahead for the next five years
    p = parameters.gov.contrib.congress.romney.family_security_act
    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).remove_head_of_household:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_remove_head_of_household()
    else:
        return None


remove_head_of_household = create_remove_head_of_household_reform(
    None, None, bypass=True
)
