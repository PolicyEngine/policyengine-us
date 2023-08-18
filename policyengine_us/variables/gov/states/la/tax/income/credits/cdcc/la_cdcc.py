from policyengine_us.model_api import *


class la_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = "http://legis.la.gov/Legis/Law.aspx?d=101769"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.credits.cdcc
        # determine LA cdcc amount
        us_cdcc = tax_unit("cdcc", period)
        us_agi = tax_unit("adjusted_gross_income", period)
        la_cdcc = us_cdcc * p.rate.calc(us_agi, right=True)
        # Cap credit at the maximum amount for filers in the upper income bracket.
        upper_bracket = us_agi > p.rate.thresholds[-1]
        upper_bracket_amount = min_(p.max_amount_upper_bracket, la_cdcc)
        return where(upper_bracket, upper_bracket_amount, la_cdcc)
