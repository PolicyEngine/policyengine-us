from policyengine_us.model_api import *


class ny_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY taxable income"
    unit = USD
    documentation = "NY AGI less taxable income deductions"
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/611"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ny_agi", period)
        deductions = tax_unit("ny_deductions", period)
        exemptions = tax_unit("ny_exemptions", period)
        return max_(0, agi - deductions - exemptions)
