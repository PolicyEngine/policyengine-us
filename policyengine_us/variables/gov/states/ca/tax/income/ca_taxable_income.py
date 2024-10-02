from policyengine_us.model_api import *


class ca_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"
        "https://www.ftb.ca.gov/forms/2022/2022-540.pdf"
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        ded = tax_unit("ca_deductions", period)
        agi = tax_unit("ca_agi", period)
        return max_(0, agi - ded)
