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
        "https://web.archive.org/web/20261009215322/https://earlychildhood.marylandpublicschools.org/child-care-providers/child-care-scholarship-program",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.msde.ccs.income
        countable_income = spm_unit("md_ccs_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        current_smi = spm_unit("hhs_smi", period)

        # Maryland holds the SMI base year on its own schedule (MSDE Feb 4, 2026
        # W&M briefing slide 21): FY2019-2022 used 2018 SMI and FY2023-2024 used
        # 2021 SMI. The scales MSDE posts moved continuing families to the
        # federal fiscal 2025 median on April 22, 2024 and new applicants on
        # December 15, 2024, and MSDE still posts both scales in October 2026.
        def monthly_smi(freeze_in_effect, frozen_year):
            if freeze_in_effect:
                return (
                    smi(size, state, f"{frozen_year}-10-01", parameters)
                    / MONTHS_IN_YEAR
                )
            return current_smi

        initial_smi = monthly_smi(p.smi_freeze_in_effect, p.smi_frozen_year)
        continuation_smi = monthly_smi(
            p.continuation_smi_freeze_in_effect, p.continuation_smi_frozen_year
        )
        enrolled = spm_unit("md_ccs_enrolled", period)
        income_limit = where(
            enrolled,
            continuation_smi * p.smi_rate.continuation,
            initial_smi * p.smi_rate.initial,
        )
        return countable_income <= income_limit
