from policyengine_us.model_api import *


class ne_adc_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska ADC countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1726"
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.adc.income
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        # Per Neb. Rev. Stat. 68-1726(3)(a)(ii): 50% of gross earned income
        # is disregarded for recipients
        return gross_earned * (1 - p.earned_income_disregard)
