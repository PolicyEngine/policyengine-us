from policyengine_us.model_api import *


class ms_ccpp_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Mississippi CCPP monthly family co-payment"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=41"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.ccpp.copay
        income_based_copay = spm_unit("ms_ccpp_income_based_copay", period)
        capped_minimum_fee_copay = min_(
            income_based_copay, p.minimum_fee_categories_cap
        )
        minimum_fee_copay = where(
            spm_unit("ms_ccpp_minimum_fee_category", period),
            capped_minimum_fee_copay,
            income_based_copay,
        )

        return where(spm_unit("ms_ccpp_copay_waived", period), 0, minimum_fee_copay)
