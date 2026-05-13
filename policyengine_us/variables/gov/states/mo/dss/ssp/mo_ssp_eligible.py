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
        # SAB applicants must apply for or receive SSI, but the grant can be
        # paid even when SSI is zero. We don't track that application
        # requirement, Missouri-specific resource limits, the closed
        # 1973-conversion State Pension cohort, or Supplemental Nursing Care
        # physician medical-need and facility-cost-versus-income tests.
        in_category = person("mo_ssp_category_eligible", period)
        age_eligible = person("mo_ssp_age_eligible", period)
        living_arrangement = person("mo_ssp_living_arrangement", period)
        is_sab = living_arrangement == living_arrangement.possible_values.SAB
        p = parameters(period).gov.states.mo.dss.ssp
        receives_ssi = person("ssi", period) > 0
        ssi_receipt_requirement_met = is_sab | receives_ssi
        countable_income = person("ssi_countable_income", period)
        sab_income_eligible = ~is_sab | (
            countable_income <= p.sab.consolidated_standard
        )
        return (
            in_category
            & age_eligible
            & ssi_receipt_requirement_met
            & sab_income_eligible
        )
