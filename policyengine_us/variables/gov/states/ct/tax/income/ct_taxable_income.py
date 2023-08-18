from policyengine_us.model_api import *


class ct_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        income = tax_unit("ct_agi", period)
        personal_exemptions = tax_unit("ct_personal_exemptions", period)
        return max_(income - personal_exemptions, 0)
