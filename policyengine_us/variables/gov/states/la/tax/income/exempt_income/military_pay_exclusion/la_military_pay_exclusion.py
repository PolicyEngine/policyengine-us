from policyengine_us.model_api import *


class la_military_pay_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana military pay exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA
    reference = "http://www.legis.la.gov/legis/Law.aspx?d=101760"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.income.exempt_income.military_pay_exclusion
        military_pay = add(tax_unit, period, ["military_service_income"])
        return min_(p.max_amount, military_pay)
