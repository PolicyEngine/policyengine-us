from policyengine_us.model_api import *


class la_cdcc_eligible_child(Variable):
    value_type = int
    entity = Person
    label = "Child eligible for the Louisiana CDCC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.credits.child_care_expense_credit

        # determine if the child is eligible for cdcc
        eligible_children = person("la_cdcc_eligible_child", period)
        child_expense_tax_credit = tax_unit(
            "la_child_expense_tax_credit", period
        )
        cdcc_eligible = eligible_children > p.age_threshold

        return where(cdcc_eligible, 0, child_expense_tax_credit)
