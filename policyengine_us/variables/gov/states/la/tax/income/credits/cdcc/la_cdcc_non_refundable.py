from policyengine_us.model_api import *


class la_cdcc_non_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana non refundable cdcc"
    unit = USD
    definition_period = YEAR
    reference = "http://legis.la.gov/Legis/Law.aspx?d=101769"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.credits
        # determine AGI eligibility
        us_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = us_agi > p.cdcc.agi_threshold
        # determine LA nonrefundable cdcc amount
        us_cdcc = tax_unit("cdcc", period)
        la_non_refundable_cdcc = us_cdcc * p.cdcc.non_refundable.rate.calc(
            us_agi
        )
        if us_agi > 60000 and la_non_refundable_cdcc > p.cdcc.non_refundable.hi_threshold:
            la_non_refundable_cdcc = p.cdcc.non_refundable.hi_threshold
        return agi_eligible * la_non_refundable_cdcc
