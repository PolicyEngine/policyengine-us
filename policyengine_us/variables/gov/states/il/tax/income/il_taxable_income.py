from policyengine_us.model_api import *


class il_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        base_income = tax_unit("il_base_income", period)
        exemptions = tax_unit("il_total_exemptions", period)
        return max_(0, base_income - exemptions)
