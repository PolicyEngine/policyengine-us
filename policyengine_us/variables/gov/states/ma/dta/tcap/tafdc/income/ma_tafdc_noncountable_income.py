from policyengine_us.model_api import *


class ma_tafdc_noncountable_income(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts TAFDC noncountable income (informational)"
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
        # Conditional exclusions per 106 CMR 704.250
        conditional = add(
            spm_unit,
            period,
            [
                "ma_tafdc_ssi_recipient_income_exclusion",
                "ma_tafdc_dependent_child_earned_income_exclusion",
                "ma_tafdc_lump_sum_income_exclusion",
                "ma_tafdc_child_support_deduction",
            ],
        )
        return unconditional + conditional
