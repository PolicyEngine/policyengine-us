from policyengine_us.model_api import *


class co_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        fed_taxinc = tax_unit("taxable_income", period)
        additions = tax_unit("co_additions", period)
        subtractions = tax_unit("co_subtractions", period)
        return max_(0, fed_taxinc + additions - subtractions)
