from policyengine_us.model_api import *


class la_child_care_expense_credit_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the Louisiana child care expense credit"
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.credits.school_readiness
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        age_eligible = age < p.age_threshold

        return dependent & age_eligible
