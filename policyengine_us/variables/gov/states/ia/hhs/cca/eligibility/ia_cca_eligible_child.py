from policyengine_us.model_api import *


class ia_cca_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Iowa CCA"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=5"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.eligibility
        # Iowa serves a child up to age 13, or up to age 19 for a child
        # with special needs (IAC 441-170.2(2)"a"). `age` is YEAR-defined.
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_eligible = where(
            is_disabled,
            age < p.special_needs_age_limit,
            age < p.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        # Child status is age-based, not tax-dependency-based. Iowa's
        # family-size definition (IAC 441-170.2(1)"e"(3)) explicitly includes
        # "a child or children who live with a person or persons not legally
        # responsible for the child's support," so a non-dependent minor
        # living with a non-parent caretaker is still an eligible child;
        # gating on is_tax_unit_dependent would wrongly exclude them.
        standard_eligible = age_eligible & immigration_eligible
        # A child in protective or foster care qualifies through the
        # income-exception path regardless of dependency or immigration
        # status (IAC 441-170.2(1)"b").
        protective = person("receives_or_needs_protective_services", period)
        foster = person("is_in_foster_care", period)
        categorical_eligible = age_eligible & (protective | foster)
        return standard_eligible | categorical_eligible
