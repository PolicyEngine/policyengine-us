from policyengine_us.model_api import *


class oh_distribution_credit_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Ohio lump sum distribution credit"
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits
        return person("age", period) >= p.senior_citizen.age_threshold
