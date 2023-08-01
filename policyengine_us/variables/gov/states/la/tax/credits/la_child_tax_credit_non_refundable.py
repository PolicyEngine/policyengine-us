from policyengine_us.model_api import *


class la_child_tax_credit_non_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana non refundable Child Expense Tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.la.tax.credits.child_care_expense_credit.rate

        # determine LA nonrefundable amount
        child_care_credit = tax_unit("la_state_child_care_credit", period)
        eligible_child = person("la_child_care_expense_credit_eligible_child", period)
        quality_rating = person(
            "quality_rating_of_child_care_facility", period
        )
        child_credit_percent = eligible_child * p.refundable.calc(quality_rating)
        amount = child_care_credit * child_credit_percent

        return tax_unit.sum(amount)
