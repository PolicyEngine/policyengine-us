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
        # ARSD 67:47:01:03(2)-(4) and Manual 4.3: a child under 18, or under 19
        # "if enrolled in school and expected to graduate", is eligible when
        # physically or mentally incapable of self-care (is_disabled proxies
        # the medical documentation) or under court supervision. School
        # enrollment proxies the graduation expectation. is_in_k12_school is
        # imputed only through age 17, so an 18-year-old still in school is
        # captured via is_in_secondary_school (as in mo_ccs_eligible_child).
        special_status = person("is_disabled", period.this_year) | person(
            "is_under_court_supervision", period.this_year
        )
        is_in_school = person("is_in_k12_school", period.this_year) | person(
            "is_in_secondary_school", period.this_year
        )
        special_needs_age_limit = where(
            is_in_school,
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
