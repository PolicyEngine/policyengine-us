from policyengine_us.model_api import *


class mo_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Missouri State Supplementary Payment"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.030",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mo.html",
    )

    def formula(person, period, parameters):
        # SAB applicants must apply for SSI but the grant is paid regardless
        # of receipt; SNC eligibility turns on the facility-cost-vs-income
        # need test, not SSI receipt. We don't track the SAB SSI-application
        # requirement, Missouri-specific resource limits, the closed
        # 1973-conversion State Pension cohort, or Supplemental Nursing Care
        # physician medical-need tests.
        in_category = person("mo_ssp_category_eligible", period)
        age_eligible = person("mo_ssp_age_eligible", period)
        living_arrangement = person("mo_ssp_living_arrangement", period)
        categories = living_arrangement.possible_values
        is_sab = living_arrangement == categories.SAB
        is_snc = (living_arrangement != categories.SAB) & (
            living_arrangement != categories.NONE
        )
        p = parameters(period).gov.states.mo.dss.ssp
        countable_income = person("ssi_countable_income", period)
        sab_income_eligible = ~is_sab | (
            countable_income <= p.sab.consolidated_standard
        )
        snc_countable_income = person("mo_snc_countable_income", period)
        facility_base_charge = person("mo_snc_facility_base_charge", period)
        snc_need_eligible = ~is_snc | (snc_countable_income < facility_base_charge)
        return in_category & age_eligible & sab_income_eligible & snc_need_eligible
