from policyengine_us.model_api import *


class il_pfae_age_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Child meets age requirements for Illinois PFAE"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/pages/preschool-for-all.aspx",
        "https://www.isbe.net/Documents/pdg-eg-grant-enrollment-form.pdf",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # PFA/PFAE serves children ages 3-4, plus 5-year-olds not yet
        # kindergarten eligible. Per 105 ILCS 5/10-20.12, children who
        # turn 5 on or before September 1 are kindergarten eligible.
        # Since PolicyEngine uses age in whole years without birth month,
        # we include all 5-year-olds as a simplification (some are eligible).
        p = parameters(period).gov.states.il.isbe.pfae.eligibility
        age = person("age", period)
        return p.age_range.calc(age)
