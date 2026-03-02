from policyengine_us.model_api import *


class ne_cdcc_nonrefundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska nonrefundable cdcc"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits
        # determine AGI eligibility
        eligible = ~tax_unit("ne_cdcc_refundable_eligible", period)
        # determine NE nonrefundable cdcc amount
        # Nebraska matches 25% of the federal credit claimed
        # (Schedule 3, line 2 of federal Form 1040)
        us_cdcc = tax_unit("cdcc", period)
        ne_cdcc = us_cdcc * p.cdcc.nonrefundable.fraction
        return eligible * ne_cdcc
