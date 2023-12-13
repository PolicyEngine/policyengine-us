from policyengine_us.model_api import *


class oh_distribution_credit_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Ohio lump sum distribution credit eligibility"
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits
        age_eligible = person("age", period) >= p.senior_citizen.age_threshold
        return age_eligible
