from policyengine_us.model_api import *
from policyengine_us.tools.tob import income_tax_with_social_security_override


class income_tax_without_social_security(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Chapter 1 income tax without taxable Social Security"
    unit = USD
    documentation = (
        "Cached chapter 1 income-tax counterfactual (after nonrefundable and "
        "before refundable credits, excluding chapter 2A net investment "
        "income tax) shared by the taxation-of-benefits revenue variables. "
        "The counterfactual branch is released after calculating the tax."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/401"

    def formula(tax_unit, period, parameters):
        return income_tax_with_social_security_override(tax_unit.simulation, period)
