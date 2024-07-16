from policyengine_us.model_api import *


class la_school_readiness_credit_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the Louisiana school readiness tax credit"
    definition_period = YEAR
    reference = "https://revenue.louisiana.gov/TaxForms/IT540WEB(2022)%20F%20D2.pdf#page=15"
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.income.credits.school_readiness
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        age_eligible = age < p.age_threshold

        return dependent & age_eligible
