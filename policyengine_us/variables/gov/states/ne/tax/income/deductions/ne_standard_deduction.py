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
        # count extra amounts for adults being elderly and/or blind
        # number of head extras
        head_extras = 0
        head_extras += tax_unit("age_head", period) >= p.age_minimum
        head_extras += tax_unit("blind_head", period)
        # number of spouse extras
        spouse_extras = 0
        spouse_extras += tax_unit("age_spouse", period) >= p.age_minimum
        spouse_extras += tax_unit("blind_spouse", period)
        spouse_extras = where(
            filing_status == filing_status.possible_values.JOINT,
            spouse_extras,
            0,
        )
        extras = head_extras + spouse_extras
        # calculate standard deduction amount
        base_ded = p.base_amount[filing_status]
        extra_ded = p.extra_amount[filing_status]
        return base_ded + extras * extra_ded
