from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_limit_salt_deduction_to_property_taxes() -> Reform:
    class salt_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "SALT deduction"
        unit = USD
        documentation = "State and local taxes plus real estate tax deduction from taxable income."
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/164"

        def formula(tax_unit, period, parameters):
            salt_amount = add(
                tax_unit,
                period,
                ["real_estate_taxes"],
            )
            salt = parameters(
                period
            ).gov.irs.deductions.itemized.salt_and_real_estate
            cap = salt.cap[tax_unit("filing_status", period)]
            return min_(cap, salt_amount)

    class reform(Reform):
        def apply(self):
            self.update_variable(salt_deduction)

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
