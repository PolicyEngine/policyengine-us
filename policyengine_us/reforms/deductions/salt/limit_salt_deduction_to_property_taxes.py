from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_limit_salt_deduction_to_property_taxes() -> Reform:
    def modify_parameters(parameters):
        parameters.gov.irs.deductions.itemized.salt_and_real_estate.sources.update(
            start=instant("2025-01-01"),
            stop=instant("2036-12-31"),
            value=["real_estate_taxes"],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def create_limit_salt_deduction_to_property_taxes_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_limit_salt_deduction_to_property_taxes()

    p = parameters.gov.contrib.deductions.salt

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).limit_salt_deduction_to_property_taxes:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_limit_salt_deduction_to_property_taxes()
    else:
        return None


limit_salt_deduction_to_property_taxes = (
    create_limit_salt_deduction_to_property_taxes_reform(
        None, None, bypass=True
    )
)
