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
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40028/40028.htm",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/ML/2025/CCAP%20ML%203909%20Effective%20May.1.2025.pdf#page=3",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.eligibility
        age = person("age", period.this_year)
        # 400-28-35-02 requires supervised care specified in a court order.
        # General court supervision alone does not satisfy that requirement.
        is_disabled = person("is_disabled", period.this_year)
        court_ordered_care = person(
            "requires_childcare_under_court_order", period.this_year
        )
        age_limit = where(
            is_disabled | court_ordered_care,
            p.disabled_child_age_limit,
            p.child_age_limit,
        )
        # A child who turns 13 mid-eligibility-period stays eligible through the
        # next review under the continuation rule. We do not track the
        # application/review month, so we use a flat
        # age < 13 cutoff instead (400-28-35-02).
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
