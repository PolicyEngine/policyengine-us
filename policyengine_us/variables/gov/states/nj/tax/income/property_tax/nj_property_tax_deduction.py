from policyengine_us.model_api import *


class nj_property_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey property tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-17/"
    defined_for = "nj_taking_property_tax_deduction"
    default_value = 0

    def formula(tax_unit, period, parameters):
        # Get the tax unit's potential property tax deduction.
        potential_deduction = tax_unit(
            "nj_potential_property_tax_deduction", period
        )

        # Get whether household is taking deduction (over credit).
        taking_deduction = tax_unit("nj_taking_property_tax_deduction", period)

        return potential_deduction * taking_deduction
