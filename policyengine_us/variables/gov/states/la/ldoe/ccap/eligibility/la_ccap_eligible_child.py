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
        disabled = person("is_disabled", period.this_year)
        # LAC 28:CLXV.503.A.2: under 13, or 13-17 and incapable of self-care.
        # The court-supervision pathway for ages 13-17 is not tracked at the moment.
        age_eligible = (age < p.child_limit) | (
            disabled & (age < p.disabled_child_limit)
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
