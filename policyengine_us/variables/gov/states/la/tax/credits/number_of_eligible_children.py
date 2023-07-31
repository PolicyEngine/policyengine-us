from policyengine_us.model_api import *


class la_cdcc_eligible_child(Variable):
    value_type = int
    entity = TaxUnit
    label = "Louisiana non-refundable Child Expense Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.credits.child_care_expense_credit

        # determine if the number of eligible children is below six
        eligible_children = tax_unit("number_of_eligible_children", period)
        child_expense_tax_credit = tax_unit(
            "la_child_expense_tax_credit", period
        )
        cdcc_eligible = eligible_children > p.children_threshold

        return where(cdcc_eligible, 0, child_expense_tax_credit)
