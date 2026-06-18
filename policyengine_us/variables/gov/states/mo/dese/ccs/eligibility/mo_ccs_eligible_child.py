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
        # "Child with special needs" (5 CSR 25-200.050(11)) covers six criteria:
        # (A) SSI receipt, (B) Missouri Department of Mental Health services,
        # (C) verified disability, (D) protective services, (E) adoption subsidy,
        # or (F) court supervision. We model (A) via SSI receipt, (C) via
        # is_disabled, and (D) via the protective-services category below.
        # (B), (E), and (F) have no PolicyEngine input and are not tracked at the
        # moment. Special-needs status also selects the special-needs rate column
        # (mo_ccs_maximum_daily_benefit) and waives the sliding fee (mo_ccs_copay).
        is_disabled = person("is_disabled", period.this_year)
        # A child receiving SSI is a child with special needs
        # (5 CSR 25-200.050(11)(A)).
        receives_ssi = person("ssi", period) > 0
        # A protective-services child is a child with special needs
        # (5 CSR 25-200.050(11)(D)) and is an eligible child up to under 19
        # regardless of school enrollment (Manual sec. 4.5(4)).
        is_protective = person("mo_ccs_protective_services", period)
        is_special_needs = is_disabled | receives_ssi | is_protective
        # Being in elementary or secondary school extends the special-needs
        # ceiling by one year (to under 19; Manual sec. 4.5(3)). is_in_k12_school
        # only fires through age 17, so an 18-year-old still in secondary school
        # is captured via is_in_secondary_school. Post-secondary/college students
        # are out of scope (the statute says "elementary or secondary school").
        is_in_school = person("is_in_k12_school", period.this_year) | person(
            "is_in_secondary_school", period.this_year
        )
        # Protective-services children reach the under-19 ceiling without the
        # school condition (Manual sec. 4.5(4)).
        extended_age = is_in_school | is_protective
        special_needs_limit = where(
            extended_age,
            p.special_needs_in_school_age_limit,
            p.special_needs_child_age_limit,
        )
        age_eligible = where(
            is_special_needs,
            age < special_needs_limit,
            age < p.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        return age_eligible & immigration_eligible & is_dependent
