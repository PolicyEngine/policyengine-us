from policyengine_us.model_api import *
from policyengine_us.tools.tob import income_tax_with_social_security_override


class income_tax_without_social_security(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax without taxable Social Security"
    unit = USD
    documentation = (
        "Cached income-tax counterfactual shared by the taxation-of-benefits "
        "revenue variables. The counterfactual branch is released after "
        "calculating income tax."
    )

    def formula(tax_unit, period, parameters):
        return income_tax_with_social_security_override(tax_unit.simulation, period)
