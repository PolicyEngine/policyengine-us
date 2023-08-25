from policyengine_us.model_api import *


class nj_property_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey property tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-17/"
    defined_for = "nj_taking_property_tax_deduction"

    def formula(tax_unit, period, parameters):
        deduction = tax_unit("nj_potential_property_tax_deduction", period)
        taking_deduction = tax_unit("nj_taking_property_tax_deduction", period)
        return deduction * taking_deduction
