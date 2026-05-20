from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class md_ccs_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maryland Child Care Scholarship (CCS) income eligible"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.03",
        "https://mgaleg.maryland.gov/2022RS/Chapters_noln/CH_525_hb0995E.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.msde.ccs.income
        countable_income = spm_unit("md_ccs_countable_income", period)
        # Maryland freezes the SMI base year on a fiscal-year schedule (MSDE
        # Feb 4, 2026 W&M briefing slide 21): FY2019-2022 used 2018 SMI,
        # FY2023-2024 used 2021 SMI, FY2025+ uses current SMI. PolicyEngine's
        # hhs_smi parameter only has data from 2021-10-01 forward, so the
        # FY2019-2022 freeze (2018 SMI) will return zero until earlier SMI
        # entries are added.
        base_year = p.smi_base_year
        if base_year > 0:
            size = spm_unit("spm_unit_size", period)
            state = spm_unit.household("state_code_str", period)
            smi_value = smi(size, state, f"{int(base_year)}-10-01", parameters)
        else:
            smi_value = spm_unit("hhs_smi", period)
        enrolled = spm_unit("md_ccs_enrolled", period)
        income_limit = where(
            enrolled,
            smi_value * p.smi_rate.continuation,
            smi_value * p.smi_rate.initial,
        )
        return countable_income <= income_limit
