from policyengine_us.model_api import *


class la_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Louisiana CCAP eligible child"
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap.age
        age = person("age", period.this_year)
        # LAC 28:CLXV.503.A.2: under 13, or 13-17 and incapable of self-care
        # (verified by a physician or by receipt of SSI). The court-supervision
        # pathway for ages 13-17 is not tracked at the moment.
        incapable = person("is_incapable_of_self_care", period.this_year)
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        older_child_eligible = (incapable | receives_ssi) & (
            age < p.disabled_child_limit
        )
        age_eligible = (age < p.child_limit) | older_child_eligible
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
