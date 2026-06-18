from policyengine_us.model_api import *


class ms_ccpp_copay_waived(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Mississippi CCPP co-payment is waived"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=40"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.ccpp.copay
        monthly_income = max_(spm_unit("ms_ccpp_countable_income", period), 0)
        at_or_below_fpl = monthly_income <= (
            spm_unit("spm_unit_fpg", period) * p.fpg_exempt_rate
        )
        homeless_no_income = spm_unit.household("is_homeless", period.this_year) & (
            monthly_income == 0
        )
        return (
            at_or_below_fpl | spm_unit("is_tanf_enrolled", period) | homeless_no_income
        )
