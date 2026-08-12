from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person.immigration_status import (
    ImmigrationStatus,
)


class sd_cca_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "South Dakota CCA eligible child"
    definition_period = MONTH
    defined_for = StateCode.SD
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/Subsidy_Manual.pdf#page=9",
        "https://sdlegislature.gov/Rules/Administrative/67:47:01:03",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.eligibility
        age = person("age", period.this_year)
        # A child under 13 is eligible. A child physically or mentally incapable
        # of self-care is eligible through age 17 (under 18), extended through
        # age 18 (under 19) when enrolled in school and expected to graduate.
        # is_disabled proxies the incapacity determination; the
        # court-supervision pathway is not modeled.
        is_disabled = person("is_disabled", period.this_year)
        is_in_school = person("is_in_k12_school", period.this_year)
        special_needs_age_limit = where(
            is_in_school,
            p.special_needs_student_age_limit,
            p.special_needs_age_limit,
        )
        age_limit = where(is_disabled, special_needs_age_limit, p.child_age_limit)
        age_eligible = age < age_limit
        # The child must be a United States citizen or a lawful permanent
        # resident, which is narrower than the federal CCDF immigration test.
        immigration_status = person("immigration_status", period.this_year)
        immigration_eligible = (immigration_status == ImmigrationStatus.CITIZEN) | (
            immigration_status == ImmigrationStatus.LEGAL_PERMANENT_RESIDENT
        )
        # The child needs a reason for care: every caretaker in an approved
        # activity, or the child receives protective services
        # (ARSD 67:47:01:03).
        reason_for_care_eligible = person("sd_cca_reason_for_care_eligible", period)
        return age_eligible & immigration_eligible & reason_for_care_eligible
