from policyengine_us.model_api import *


class ma_tafdc_noncountable_income(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts TAFDC noncountable income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts"
        "/106-CMR-704-250"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        # Unconditional exclusions: benefits that are always
        # noncountable (SNAP, WIC, housing subsidies, etc.)
        unconditional = add(
            spm_unit,
            period,
            parameters(
                period
            ).gov.states.ma.dta.tcap.tafdc.income.noncountable.sources,
        )
        # Conditional exclusions
        # (A) SSI recipient income
        ssi = add(
            spm_unit,
            period,
            [
                "ma_tafdc_ssi_recipient_income_exclusion",
            ],
        )
        # (U) Dependent child earned income
        child = add(
            spm_unit,
            period,
            [
                "ma_tafdc_dependent_child_earned_income_exclusion",
            ],
        )
        # (B) Lump sum income exclusion
        lump_sum = add(
            spm_unit,
            period,
            ["ma_tafdc_lump_sum_income_exclusion"],
        )
        # (GG) Child support pass-through (already in
        # deductions pipeline but counted here for
        # informational purposes)
        child_support = add(
            spm_unit,
            period,
            ["ma_tafdc_child_support_deduction"],
        )
        conditional = ssi + child + lump_sum + child_support
        return unconditional + conditional
