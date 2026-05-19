from policyengine_us.model_api import *


class il_liheap_income_bracket(Variable):
    value_type = int
    entity = SPMUnit
    label = "Income bracket for IL LIHEAP payment (1-4)"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://liheapch.acf.gov/docs/2024/benefits-matricies/IL_BenefitMatrix_2024.pdf#page=1"

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        fpg = spm_unit("spm_unit_fpg", period)
        income_as_fpg_share = where(fpg > 0, income / fpg, 0)
        # Clamp negative income to bracket 1 (0-50% FPL).
        pct_fpg = max_(income_as_fpg_share, 0)
        p = parameters(period).gov.states.il.dceo.liheap.payment
        return p.income_bracket.calc(pct_fpg)
