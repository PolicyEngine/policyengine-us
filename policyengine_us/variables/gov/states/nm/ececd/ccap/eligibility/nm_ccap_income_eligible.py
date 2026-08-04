from policyengine_us.model_api import *


class nm_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New Mexico CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.NM
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.015.0002.html",
        "https://www.nmececd.org/universal/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.ececd.ccap.eligibility
        # Universal Child Care removes the income limit from November 1, 2025:
        # families are income-eligible regardless of income from that date.
        if not p.income_limit_in_effect:
            return True
        # 8.15.2.9 / 8.15.2.12 codify an initial cap of 200% FPL and a
        # continuation cap of 250% FPL, but ECECD has operated at broader
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
        # 8.15.2.9 Priority 2: families transitioning off TANF need not meet
        # the income test. is_tanf_enrolled is a bare input that breaks the
        # CCAP <-> TANF circular dependency.
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return is_tanf | fpl_eligible
