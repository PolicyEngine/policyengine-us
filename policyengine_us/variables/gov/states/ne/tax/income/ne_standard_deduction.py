from policyengine_us.model_api import *


class ne_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ne.tax.income.deductions.standard
        base_ded_amount = p.base_amount[filing_status]
        extra_ded_amount = p.extra_amount[filing_status]
        extras = tax_unit("aged_blind_count", period)
        return base_ded_amount + extras * extra_ded_amount
