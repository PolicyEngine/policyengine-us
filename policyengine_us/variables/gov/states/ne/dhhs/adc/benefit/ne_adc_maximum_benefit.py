from policyengine_us.model_api import *


class ne_adc_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska ADC maximum benefit before unearned income deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1713",
        "https://dhhs.ne.gov/Pages/Title-468.aspx",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        need_standard = spm_unit("ne_adc_need_standard", period)
        countable_earned = spm_unit("ne_adc_countable_earned_income", period)
        payment_standard = spm_unit("ne_adc_payment_standard", period)
        # Gap budgeting: Gap = Standard of Need - Net Earned Income
        gap = max_(need_standard - countable_earned, 0)
        # Benefit = min(Gap, Payment Standard)
        return min_(gap, payment_standard)
