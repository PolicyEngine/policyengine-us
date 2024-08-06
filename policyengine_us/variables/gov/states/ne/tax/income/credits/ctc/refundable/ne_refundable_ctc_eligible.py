from policyengine_us.model_api import *


class ne_refundable_ctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Nebraska refundable Child Tax Credit"
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/about/2023-nebraska-legislative-changes"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.ctc.refundable
        fpg = tax_unit("tax_unit_fpg", period)
        income_limit = fpg * p.fpg_fraction
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        return adjusted_gross_income <= income_limit
