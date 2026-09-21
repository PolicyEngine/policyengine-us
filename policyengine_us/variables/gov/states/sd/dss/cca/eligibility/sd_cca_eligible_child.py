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
        "https://dss.sd.gov/docs/childcare/assistance/BEES_CCA_Policy_Manual.pdf#page=18",
        "https://sdlegislature.gov/Rules/Administrative/67:47:01:03",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.eligibility
        age = person("age", period.this_year)
        # ARSD 67:47:01:03(2)-(4) applies the same age and school conditions
        # to incapacity and court supervision. Expected graduation defaults
        # to K-12 enrollment unless overridden per person.
        special_status = person("is_disabled", period.this_year) | person(
            "is_under_court_supervision", period.this_year
        )
        graduating_student = person("is_in_k12_school", period.this_year) & person(
            "sd_cca_expected_to_graduate", period.this_year
        )
        special_needs_age_limit = where(
            graduating_student,
            p.special_needs_student_age_limit,
            p.special_needs_age_limit,
        )
        age_limit = where(special_status, special_needs_age_limit, p.child_age_limit)
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
