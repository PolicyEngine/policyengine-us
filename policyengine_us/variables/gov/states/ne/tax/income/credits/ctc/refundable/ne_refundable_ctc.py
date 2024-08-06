from policyengine_us.model_api import *


class ne_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska refundable Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/about/2023-nebraska-legislative-changes"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.ctc.refundable

        fpg = tax_unit("tax_unit_fpg", period)
        income_limit = fpg * p.income_fraction
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        income_eligible = adjusted_gross_income <= income_limit
        credit_amount = p.amount.calc(adjusted_gross_income)

        person = tax_unit.members
        qualifying_child = person("ne_refundable_ctc_eligible_child", period)
        qualifying_children = tax_unit.sum(qualifying_child)

        return where(income_eligible, credit_amount * qualifying_children, 0)
