from policyengine_us.model_api import *


class nm_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New Mexico CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.NM
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.015.0002.html",
        "https://www.srca.nm.gov/parts/title08/08.009.0003.html",
        "https://www.nmececd.org/wp-content/uploads/2025/11/8.9.3_integrated_FULL-TEXT.pdf#page=6",
        # PDF pages 9, 12
        "https://prod-rf-lambda.rtssaas.com/PublicFiles/d89c47bd0d70402dba89b03a22bda6d1/b0e207a9-a1a3-412d-9660-0a6e925f6f25/8.9.3.pdf#page=9",
        "https://www.nmececd.org/universal/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.ececd.ccap.eligibility
        # Universal Child Care removes the income limit from November 1, 2025:
        # families are income-eligible regardless of income from that date.
        # The 2025-11-04 amendment added category four C with no income cap
        # (8.9.3.9.H), and the rule that replaced 8.9.3 NMAC on 2026-09-09 sets
        # no income limit.
        if not p.income_limit_in_effect:
            return True
        # 8.15.2.9 / 8.15.2.12 (8.9.3.9 / 8.9.3.12 from 2022-11-01) codify an
        # initial cap of 200% FPL and a continuation cap of 250% FPL (400% /
        # 425% for essential workers), but ECECD has operated at broader
        # ceilings since 2022-05-01 (400% initial / 425% continuation per the
        # LFC brief). fpl_limit.initial / .continuation carry those operative
        # values by date, so this formula uses whichever ceiling was in force.
        countable_income = spm_unit("nm_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        enrolled = spm_unit("nm_ccap_enrolled", period)
        income_limit = fpg * where(
            enrolled, p.fpl_limit.continuation, p.fpl_limit.initial
        )
        fpl_eligible = countable_income <= income_limit
        # 8.15.2.9.D Priority 2 (8.9.3.9.D from 2022-11-01): families
        # transitioning off TANF need not meet the income test.
        # is_tanf_enrolled is a bare input that breaks the CCAP <-> TANF
        # circular dependency.
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return is_tanf | fpl_eligible
