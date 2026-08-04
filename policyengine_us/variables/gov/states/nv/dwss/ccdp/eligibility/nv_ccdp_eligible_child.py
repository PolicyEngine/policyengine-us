from policyengine_us.model_api import *


class nv_ccdp_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Nevada CCDP"
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=36"

    def formula(person, period, parameters):
        # MS 210: child must be under 13. MS 211: a child with a special need
        # is eligible up to age 19. We don't track 12-month certification
        # periods at the moment, so the mid-certification continuity that lets
        # a child age past 13 (or 19) keep coverage (MS 210/211) is not modeled.
        p = parameters(period).gov.states.nv.dwss.ccdp.eligibility
        age = person("age", period.this_year)
        # MS 211 defines a special need as a physical or mental condition that
        # severely limits self-care, or an at-risk emotional condition; broader
        # than developmental delay alone, so OR in the general disability flag.
        has_special_need = person("has_developmental_delay", period.this_year) | person(
            "is_disabled", period.this_year
        )
        age_eligible = where(
            has_special_need,
            age < p.special_needs_child_age_limit,
            age < p.child_age_limit,
        )
        # MS 214: the child (not the parent) must be a U.S. citizen or
        # lawfully-admitted non-citizen. Reuse the federal CCDF child check.
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
