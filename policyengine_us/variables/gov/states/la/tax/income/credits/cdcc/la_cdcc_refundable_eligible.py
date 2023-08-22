from policyengine_us.model_api import *


class la_cdcc_refundable_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Eligible for the refundable Louisiana Child and Dependent Care Credit"
    )
    definition_period = YEAR
    reference = "http://legis.la.gov/Legis/Law.aspx?d=101769"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        income_limit = parameters(
            period
        ).gov.states.la.tax.income.credits.cdcc.refundable_income_limit
        us_agi = tax_unit("adjusted_gross_income", period)
        return us_agi <= income_limit
