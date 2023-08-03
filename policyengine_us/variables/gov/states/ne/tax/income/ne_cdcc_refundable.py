from policyengine_us.model_api import *


class ne_cdcc_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE refundable cdcc"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_2441n.pdf"
        "https://revenue.nebraska.gov/sites/revenue.nebraska.gov/files/doc/Form_2441N_Ne_Child_and_Dependent_Care_Expenses_8-618-2022_final_2.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits
        # determine AGI eligibility
        us_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = us_agi <= p.cdcc.agi_threshold
        # determine NE refundable cdcc amount
        us_cdcc = tax_unit("cdcc", period)
        ne_cdcc = us_cdcc * p.cdcc.refundable.fraction.calc(us_agi)
        return agi_eligible * ne_cdcc
