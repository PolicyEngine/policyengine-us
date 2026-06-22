from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person.immigration_status import (
    ImmigrationStatus,
)


class nd_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "North Dakota CCAP eligible child"
    definition_period = MONTH
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.eligibility
        age = person("age", period.this_year)
        # Children with a disability (or who need supervised care under a court
        # order) remain eligible through the higher special-needs age limit.
        # is_disabled proxies the manual's special-needs status; the
        # court-order pathway is not tracked at the moment (400-28-35-02).
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.disabled_child_age_limit, p.child_age_limit)
        age_eligible = age < age_limit
        # The child (not the caretaker) must be a United States citizen or an
        # alien lawfully admitted for permanent residence (400-28-50-25). This
        # is narrower than the federal CCDF immigration test, so we do not
        # reuse is_ccdf_immigration_eligible_child.
        immigration_status = person("immigration_status", period.this_year)
        immigration_eligible = (immigration_status == ImmigrationStatus.CITIZEN) | (
            immigration_status == ImmigrationStatus.LEGAL_PERMANENT_RESIDENT
        )
        return age_eligible & immigration_eligible
