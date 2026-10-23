from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class me_heap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Maine HEAP annual income limit"
    defined_for = StateCode.ME
    reference = (
        "https://www.mainehousing.org/docs/default-source/msha-rules/ch24-home-energy-assistance-program-rule.pdf#page=11",
        "https://liheapch.acf.gov/docs/2026/state-plans/ME_Plan_2026.pdf#page=9",
        "https://www.mainehousing.org/charts/",
        "https://web.archive.org/web/20251101091454id_/https://www.mainehousing.org/programs-services/energy/energydetails/liheap",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.me.msha.heap
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("me_heap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        state = spm_unit.household("state_code_str", period)
        guideline = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        # The federal maximum, the greater of 150% of the poverty guideline and
        # 60% of state median income (42 U.S.C. 8624(b)(2)(B)), reproduces
        # MaineHousing's published 2025-26 and 2026-27 income charts.
        smi_limit = liheap_smi_limit(size, state, p_hhs.smi_limit, period, parameters)
        limit = max_(guideline * p_hhs.fpg_limit, smi_limit)
        return where(size > 0, limit, 0)
