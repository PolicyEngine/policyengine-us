from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class mt_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Montana LIHEAP annual income limit"
    defined_for = StateCode.MT
    reference = (
        "https://rules.mt.gov/policy-library-documents/application/pdf/b2d910910cc1ecf830fc66d844708df2504ed257f556ce252cc3b4d25dc84a88#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/f314cbda8448e499b69120f0401d35836fe02c4884e961091b2d56c86e3b1abc#page=1",
        # PDF pages 30, 123-124
        "https://web.archive.org/web/20260915040544/https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=30",
        # PDF pages 30, 125-126
        "https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=30",
        "https://liheapch.acf.gov/docs/2026/state-plans/MT_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.liheap.eligibility
        size = spm_unit("mt_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        state_group = spm_unit.household("state_group_str", period)
        # The published 2025-2026 and 2026-2027 tables equal the greater of
        # 60% of state median income and 150% of the prior-year poverty
        # guideline at every size; see smi_rate.yaml for the size-9 wording.
        smi_limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        fpg_limit = guideline * p.fpg_rate
        return where(size > 0, max_(smi_limit, fpg_limit), 0)
