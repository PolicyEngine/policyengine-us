from policyengine_us.model_api import *


class mo_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Missouri State Supplementary Payment"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.030",
        "https://revisor.mo.gov/main/OneSection.aspx?section=209.040",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mo.html",
    )

    def formula(person, period, parameters):
        # Missouri requires actual receipt of a federal SSI payment under 13
        # CSR 40-2.130; ssi > 0 already implies categorical / resource /
        # immigration eligibility plus the federal income test and takeup.
        # We don't track Missouri-specific resource limits, the closed
        # 1973-conversion State Pension cohort, the Supplemental Aid to the
        # Blind earned-income-limit calculation method, or the Supplemental
        # Nursing Care physician medical-need or facility-cost-versus-income
        # tests at the moment.
        receives_ssi = person("ssi", period) > 0
        in_category = person("mo_ssp_category_eligible", period)
        age_eligible = person("mo_ssp_age_eligible", period)
        living_arrangement = person("mo_ssp_living_arrangement", period)
        is_sab = living_arrangement == living_arrangement.possible_values.SAB
        p = parameters(period).gov.states.mo.dss.ssp
        non_ssi_income = (
            person("ssi_earned_income", period)
            + person("ssi_unearned_income", period)
            - person("ssi", period)
        )
        income_gate = ~is_sab | (non_ssi_income <= p.sab.income_limit)
        return receives_ssi & in_category & age_eligible & income_gate
