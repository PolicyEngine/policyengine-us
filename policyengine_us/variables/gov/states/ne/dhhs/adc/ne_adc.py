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
        p = parameters(period).gov.states.ne.dhhs.adc
        maximum_benefit = spm_unit("ne_adc_maximum_benefit", period)
        unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        # Final benefit = max benefit - unearned income
        benefit_before_minimum = max_(maximum_benefit - unearned, 0)
        # Per Neb. Rev. Stat. 43-512: no payments less than $10/month
        # If benefit > 0 but < $10, return $10; if benefit = 0, return 0
        return where(
            benefit_before_minimum > 0,
            max_(benefit_before_minimum, p.min_payment),
            0,
        )
