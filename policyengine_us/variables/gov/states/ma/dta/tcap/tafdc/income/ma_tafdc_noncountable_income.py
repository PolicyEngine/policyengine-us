from policyengine_us.model_api import *


class ma_tafdc_noncountable_income(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts TAFDC noncountable income (informational)"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-250"
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        # Unconditional exclusions: benefits that are always
        # noncountable (SNAP, WIC, housing subsidies, etc.)
        unconditional = add(
            spm_unit,
            period,
            parameters(period).gov.states.ma.dta.tcap.tafdc.income.noncountable.sources,
        )
        # Use overlap-resolved differences from gross to avoid double-counting
        # exclusions that can apply to the same income, such as SSI and
        # dependent-child earned-income exclusions.
        earned_excluded = add(spm_unit, period, ["ma_tcap_gross_earned_income"]) - add(
            spm_unit, period, ["ma_tafdc_gross_earned_income"]
        )
        unearned_excluded = add(
            spm_unit,
            period,
            ["ma_tcap_gross_unearned_income", "ma_tafdc_lump_sum_income"],
        ) - add(spm_unit, period, ["ma_tafdc_gross_unearned_income"])
        return (
            unconditional
            + max_(earned_excluded, 0)
            + max_(unearned_excluded, 0)
        )
