from policyengine_us.model_api import *


class in_ssp_rcap_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Indiana Residential Care Assistance Program"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/in.html",
        "https://law.justia.com/codes/indiana/title-12/article-10/chapter-6/section-12-10-6-2-1/",
    )

    def formula(person, period, parameters):
        # SSA 2011: "adult Medicaid or SSI recipients who, because of
        # age, blindness, or disability, are unable to reside in their
        # own home and need care in a residential facility."
        # Indiana RCAP page: "at least 65 years of age, or blind or disabled."
        is_abd = person("is_ssi_aged_blind_disabled", period.this_year)
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        # RCAP goes only to the aged, blind or disabled. People aged 65 or
        # over are outside the under-65 adult group in 42 U.S.C.
        # 1396a(a)(10)(A)(i)(VIII), and the blind or disabled are specified
        # excluded individuals under 1396a(xx)(9)(A)(ii)(V)(aa), so the
        # community engagement requirement reaches no RCAP recipient.
        # Reading Medicaid enrollment before work requirements is therefore
        # exact, and it keeps this payment out of the Medicaid -> SNAP ->
        # state supplement cycle that opens in 2027 (issue #9534).
        on_medicaid = person(
            "medicaid_enrolled_before_work_requirements", period.this_year
        )
        is_recipient = receives_ssi | on_medicaid
        age = person("age", period.this_year)
        p = parameters(period).gov.states["in"].fssa.ssp
        age_eligible = age >= p.age_threshold
        living_arrangement = person("in_ssp_living_arrangement", period)
        arrangements = living_arrangement.possible_values
        in_residential = (living_arrangement == arrangements.LICENSED_RESIDENTIAL) | (
            living_arrangement == arrangements.UNLICENSED_RESIDENTIAL
        )
        return is_abd & is_recipient & age_eligible & in_residential
