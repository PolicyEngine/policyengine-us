from policyengine_us.model_api import *


class mo_ccs_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Missouri Child Care Subsidy"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-050",
        "https://web.archive.org/web/20211208073247id_/https://dese.mo.gov/childhood/quality-programs/child-care-subsidy/child-care-manual/2010/005/00",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mo.dese.ccs.eligibility
        age = person("age", period.this_year)
        # "Child with special needs" (5 CSR 25-200.050) covers six criteria:
        # SSI receipt, mental-health services, verified disability, protective
        # services, adoption subsidy, or court supervision. We approximate it
        # with is_disabled (verified disability); the other pathways are not
        # tracked at the moment. is_disabled also selects the special-needs rate
        # column (mo_ccs_maximum_daily_benefit) and waives the sliding fee
        # (mo_ccs_copay).
        is_disabled = person("is_disabled", period.this_year)
        is_in_school = person("is_in_k12_school", period.this_year)
        # A child with special needs is eligible to a higher age, extended by
        # one year while still in school.
        special_needs_limit = where(
            is_in_school,
            p.special_needs_in_school_age_limit,
            p.special_needs_child_age_limit,
        )
        age_eligible = where(
            is_disabled,
            age < special_needs_limit,
            age < p.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        return age_eligible & immigration_eligible & is_dependent
