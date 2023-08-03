from policyengine_us.model_api import *


class me_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine taxable income"
    unit = USD
    documentation = "ME AGI less taxable income deductions"
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/611"
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        agi = tax_unit("me_agi", period)
        deductions = tax_unit("me_deductions", period)
        exemptions = tax_unit("me_exemptions", period)
        return max_(0, agi - deductions - exemptions)
