from policyengine_us.model_api import *


class ks_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        base_amt = p.base_amount[filing_status]
        aged_blind_count = tax_unit("aged_blind_count", period)
        extra_amt = aged_blind_count * p.extra_amount[filing_status]
        return base_amt + extra_amt
