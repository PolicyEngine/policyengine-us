from policyengine_us.model_api import *


class ne_adc_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska ADC countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1726",
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1713",
    )
    defined_for = StateCode.NE
    adds = [
        "ne_adc_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
