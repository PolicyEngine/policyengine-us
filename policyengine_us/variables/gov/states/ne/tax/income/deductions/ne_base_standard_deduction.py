from policyengine_us.model_api import *


class ne_base_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska standard deduction"
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
        return p.base_amount[filing_status]
