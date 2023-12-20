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
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ca.tax.income
        std_ded = p.deductions.standard.amount[filing_status]
        itm_ded = tax_unit("ca_itemized_deductions", period)
        ded = where(itm_ded > std_ded, itm_ded, std_ded)
        agi = tax_unit("ca_agi", period)
        return max_(0, agi - ded)
