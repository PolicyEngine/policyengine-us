from policyengine_us.model_api import *


class ne_adc(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska Aid to Dependent Children (ADC)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=43-512",
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1713",
    )
    defined_for = "ne_adc_eligible"

    def formula(spm_unit, period, parameters):
        maximum_benefit = spm_unit("ne_adc_maximum_benefit", period)
        unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        benefit = max_(maximum_benefit - unearned, 0)
        return min_(benefit, maximum_benefit)
