from policyengine_us.model_api import *


class la_cdcc_non_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana non-refundable Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = "http://legis.la.gov/Legis/Law.aspx?d=101769"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):

        p = parameters(period).gov.states.la.tax.income.credits.cdcc
        us_agi = tax_unit("adjusted_gross_income", period)
        # determine LA nonrefundable cdcc amount
        la_cdcc_pre_cap = tax_unit("la_cdcc", period)

        upper_bracket = (
            us_agi > p.non_refundable.upper_bracket.income_threshold
        )
        upper_bracket_amount = min_(
            p.non_refundable.upper_bracket.max_amount,
            la_cdcc_pre_cap,
        )
        la_non_refundable_cdcc = where(
            upper_bracket, upper_bracket_amount, la_cdcc_pre_cap
        )
        eligible = ~tax_unit("la_cdcc_refundable_eligible", period)
        return eligible * la_non_refundable_cdcc
