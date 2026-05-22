from policyengine_us.model_api import *


class ct_ssp_categorically_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Connecticut SSP categorically eligible"
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://www.cga.ct.gov/current/pub/chap_319s.htm#sec_17b-600",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        # Per CGS 17b-600: Must be SSI-eligible (ABD + resources + immigration).
        # No uncapped_ssi > 0 check: SSA 2011 footnote 1 states that
        # CT SSP "Includes payments made to some non-SSI recipients
        # who meet state eligibility criteria, but do not meet
        # federal SSI eligibility guidelines."
        # https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html
        is_ssi_eligible = person("is_ssi_eligible", period.this_year)

        # Per CGS 17b-600: Only blind children are eligible; disabled
        # (non-blind) children are excluded from CT SSP.
        is_child = person("is_child", period.this_year)
        is_blind = person("is_blind", period.this_year)
        is_child_excluded = is_child & ~is_blind

        return is_ssi_eligible & ~is_child_excluded
