from policyengine_us.model_api import *


class ms_ccpp_income_based_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Mississippi CCPP monthly income-based co-payment"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=41"

    def formula(spm_unit, period, parameters):
        # NOTE: Applies the published rate to exact monthly income, not to the
        # fee scale's rounded $1,000 income rows.
        p = parameters(period).gov.states.ms.dhs.ccpp.copay
        p_income = parameters(period).gov.states.ms.dhs.ccpp.income
        monthly_income = max_(spm_unit("ms_ccpp_countable_income", period), 0)
        fee_scale_size = min_(
            spm_unit("spm_unit_size", period.this_year), p.max_family_size
        )
        monthly_smi = spm_unit("hhs_smi", period)
        very_low_income = (
            monthly_income <= monthly_smi * p_income.very_low_income_smi_rate
        )
        copay_rate = where(
            very_low_income,
            p.rate.very_low_income.calc(fee_scale_size),
            p.rate.low_income.calc(fee_scale_size),
        )
        return monthly_income * copay_rate
