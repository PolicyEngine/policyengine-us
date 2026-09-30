from policyengine_us.model_api import *


class ky_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Kentucky LIHEAP income eligibility"
    defined_for = StateCode.KY
    reference = "https://www.mkcap.org/uploads/3/4/8/3/34834615/2025-2026-liheap-fact-sheet-v2.jpg"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.chfs.liheap
        size = spm_unit("spm_unit_size", period)
        fpg = spm_unit("ky_liheap_fpg", period)
        state_group = spm_unit.household("state_group_str", period)
        fpg_year = period.start.year - int(p.fpg_year_lag)
        additional_fpg = parameters(f"{fpg_year}-01-01").gov.hhs.fpg.additional_person[
            state_group
        ]
        extra = max_(size - p.maximum_table_size, 0)
        # The fact sheet specifies $688 above size eight. The workbook's $687
        # extension conflicts with that explicit eligibility instruction.
        table_fpg = fpg - extra * additional_fpg
        monthly_limit = (
            np.ceil(table_fpg * p.income_limit / MONTHS_IN_YEAR)
            + extra * p.additional_person_income_limit
        )
        income = spm_unit("ky_liheap_income", period) / MONTHS_IN_YEAR
        return income <= monthly_limit
