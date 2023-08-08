from policyengine_us.model_api import *


class la_cdcc_non_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana non-refundable CDCC"
    unit = USD
    definition_period = YEAR
    reference = "http://legis.la.gov/Legis/Law.aspx?d=101769"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.credits.cdcc
        # determine AGI eligibility
        us_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = us_agi > p.refundable_income_limit
        # determine LA nonrefundable cdcc amount
        us_cdcc = tax_unit("cdcc", period)
        la_non_refundable_cdcc_pre_cap = us_cdcc * p.non_refundable.rate.calc(
            us_agi
        )
        upper_bracket = (
            us_agi > p.non_refundable.upper_bracket.income_threshold
        )
        upper_bracket_amount = min_(
            p.non_refundable.upper_bracket.max_amount,
            la_non_refundable_cdcc_pre_cap,
        )
        la_non_refundable_cdcc = where(
            upper_bracket, upper_bracket_amount, la_non_refundable_cdcc_pre_cap
        )
        return agi_eligible * la_non_refundable_cdcc
