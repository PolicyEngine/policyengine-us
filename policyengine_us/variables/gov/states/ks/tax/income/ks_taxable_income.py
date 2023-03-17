from policyengine_us.model_api import *


class ks_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "KS taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/k-4021.pdf"
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/k-4022.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    """
    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ca.tax.income
        std_ded = p.deductions.standard.amount[filing_status]
        itm_ded = tax_unit("ks_itemized_deductions", period)
        ded = where(itm_ded > std_ded, itm_ded, std_ded)
        agi = tax_unit("ks_agi", period)
        return max_(0, agi - ded)
    """
