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
        # Children ages 3-5 (before kindergarten) are eligible for PFAE.
        # 23 IAC § 235.10 defines eligible children as "at-risk children age 3
        # through the age of eligibility for kindergarten."
        p = parameters(period).gov.states.il.isbe.pfae.eligibility
        age = person("age", period)
        return p.age_range.calc(age)
