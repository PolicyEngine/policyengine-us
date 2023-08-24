from policyengine_us.model_api import *


class la_child_expense_tax_credit_refundable_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana non-refundable Child Expense Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.credits.school_readiness
        # determine if it is nonrefundable or refundable
        us_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = us_agi <= p.income_threshold

        return agi_eligible
