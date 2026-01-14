from policyengine_us.model_api import *
from policyengine_us.reforms.utils import create_reform_if_active


def create_remove_head_of_household() -> Reform:
    class reform(Reform):
        def apply(self):
            self.neutralize_variable("head_of_household_eligible")

    return reform


def create_remove_head_of_household_reform(
    parameters, period, bypass: bool = False
):
    return create_reform_if_active(
        parameters,
        period,
        "gov.contrib.congress.romney.family_security_act",
        "remove_head_of_household",
        create_remove_head_of_household,
        bypass,
    )


remove_head_of_household = create_remove_head_of_household_reform(
    None, None, bypass=True
)
