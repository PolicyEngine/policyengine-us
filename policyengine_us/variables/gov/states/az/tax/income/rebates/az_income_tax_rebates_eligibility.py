from policyengine_us.model_api import *


class az_income_tax_rebates_eligibility(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Arizona one-time families tax rebates eligibility"
    documentation = "https://211arizona.org/wp-content/uploads/2023/11/Arizona-Families-Tax-Rebate.pdf"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        return tax_unit("az_dependent_tax_credit", period) > 0
