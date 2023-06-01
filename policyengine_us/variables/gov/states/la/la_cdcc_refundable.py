from policyengine_us.model_api import *


class la_cdcc_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana refundable cdcc"
    unit = USD
    definition_period = YEAR
    reference = "http://legis.la.gov/Legis/Law.aspx?d=101769"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.credits
        # determine AGI eligibility
        us_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = us_agi <= p.cdcc.agi_threshold
        # determine LA refundable cdcc amount
        us_cdcc = tax_unit("cdcc", period)
        la_cdcc = us_cdcc * p.cdcc.refundable.fraction
        return agi_eligible * la_cdcc
