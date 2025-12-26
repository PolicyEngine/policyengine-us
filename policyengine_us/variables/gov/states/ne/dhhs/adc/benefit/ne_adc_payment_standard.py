from policyengine_us.model_api import *


class ne_adc_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska ADC payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=43-512"
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.adc
        need_standard = spm_unit("ne_adc_need_standard", period)
        # Per Neb. Rev. Stat. 43-512: payment is 55% of standard of need
        return need_standard * p.benefit.payment_standard_rate
