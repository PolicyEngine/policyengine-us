from policyengine_us.model_api import *


class md_ccs_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Maryland Child Care Scholarship (CCS) countable income"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.03",
        "https://mgaleg.maryland.gov/2022RS/Chapters_noln/CH_525_hb0995E.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.msde.ccs.income
        sources_income = add(
            spm_unit,
            period,
            p.countable_income.sources,
        )
        self_employment_income = add(spm_unit, period, ["self_employment_income"])
        return sources_income + self_employment_income * (
            1 - p.self_employment_deduction_rate
        )
