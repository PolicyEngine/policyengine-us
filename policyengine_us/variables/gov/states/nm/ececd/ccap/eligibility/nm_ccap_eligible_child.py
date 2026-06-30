from policyengine_us.model_api import *


class nm_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for New Mexico CCAP"
    definition_period = MONTH
    defined_for = StateCode.NM
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.015.0002.html",
        "https://www.law.cornell.edu/cfr/text/45/98.20",
    )

    def formula(person, period, parameters):
        # 8.15.2.11.F: eligible from 6 weeks old through the day before the
        # 13th birthday. The 6-week lower bound is not modeled because we don't
        # track sub-year age granularity at the moment (all children under 1
        # read age == 0), so enforcing it would wrongly exclude every infant.
        # 8.15.2.11.G: extended to under 18 for children needing special
        # supervision. We model the medical/treatment-professional branch via
        # has_developmental_delay; the court-supervision branch is not tracked
        # at the moment.
        p = parameters(period).gov.states.nm.ececd.ccap.eligibility
        age = person("age", period.this_year)
        has_developmental_delay = person("has_developmental_delay", period.this_year)
        age_eligible = where(
            has_developmental_delay,
            age < p.special_needs_child_age_limit,
            age < p.child_age_limit,
        )
        # 8.15.2.11.E: before Universal Child Care, a child must be a citizen or
        # qualified immigrant. Under Universal Child Care (from 2025-11-01) this
        # bar is removed: a participating child without a federally eligible
        # status is served with state funds, so status only sets the funding
        # source, not eligibility (ECECD Universal Child Care).
        if p.immigration_test_in_effect:
            immigration_eligible = person(
                "is_ccdf_immigration_eligible_child", period.this_year
            )
            return age_eligible & immigration_eligible
        return age_eligible
