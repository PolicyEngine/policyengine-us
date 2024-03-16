from policyengine_us.model_api import *


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

    p = parameters(period).gov.contrib.congress.romney.family_security_act

    if p.remove_head_of_household:
        return create_remove_head_of_household()
    else:
        return None


remove_head_of_household = create_remove_head_of_household_reform(
    None, None, bypass=True
)
