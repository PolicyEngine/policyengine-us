from policyengine_us.model_api import *


class ne_adc_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska ADC standard of need"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=43-513",
        "https://dhhs.ne.gov/Pages/Title-468.aspx",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.adc
        size = spm_unit("spm_unit_size", period)
        # Cap size at maximum defined in parameter table (14)
        capped_size = min_(size, 14)
        return p.need_standard[capped_size]
