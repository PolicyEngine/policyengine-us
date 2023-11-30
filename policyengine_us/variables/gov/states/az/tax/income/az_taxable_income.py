from policyengine_us.model_api import *


class az_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona taxable income"
    unit = USD
    documentation = "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140Ai.pdf#page=8https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140Ai.pdf#page=8"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        az_agi = tax_unit("az_agi", period)
        deductions = tax_unit("az_deductions", period)
        return max_(0, az_agi - deductions)
