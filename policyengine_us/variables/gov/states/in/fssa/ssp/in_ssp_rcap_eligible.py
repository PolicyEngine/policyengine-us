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
        receives_ssi = person("ssi", period.this_year) > 0
        on_medicaid = person("medicaid_enrolled", period.this_year)
        is_recipient = receives_ssi | on_medicaid
        age = person("age", period.this_year)
        p = parameters(period).gov.states["in"].fssa.ssp
        age_eligible = age >= p.age_threshold
        living_arrangement = person("in_ssp_living_arrangement", period.this_year)
        arrangements = living_arrangement.possible_values
        in_residential = (living_arrangement == arrangements.LICENSED_RESIDENTIAL) | (
            living_arrangement == arrangements.UNLICENSED_RESIDENTIAL
        )
        return is_abd & is_recipient & age_eligible & in_residential
