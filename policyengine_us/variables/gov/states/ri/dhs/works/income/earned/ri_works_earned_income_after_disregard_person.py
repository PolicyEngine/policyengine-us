from policyengine_us.model_api import *


class ri_works_earned_income_after_disregard_person(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island Works earned income after disregard per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15",
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
    )
    defined_for = StateCode.RI

    def formula(person, period, parameters):
        # Per 218-RICR-20-00-2.15: Disregard $525 + 50% of remainder
        # "This disregard is allowed for each individual who has
        # otherwise been found eligible to receive cash assistance."
        p = parameters(
            period
        ).gov.states.ri.dhs.works.income.earned_income_disregard
        gross_earned = person("tanf_gross_earned_income", period)
        after_flat_disregard = max_(gross_earned - p.amount, 0)
        return after_flat_disregard * (1 - p.rate)
