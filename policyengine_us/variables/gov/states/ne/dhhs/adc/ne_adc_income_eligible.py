from policyengine_us.model_api import *


class ne_adc_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Nebraska ADC income eligible"
    definition_period = MONTH
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1726",
        "https://dhhs.ne.gov/Pages/Title-468.aspx",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        # Per 468 NAC: countable income must be below standard of need
        countable_earned = spm_unit("ne_adc_countable_earned_income", period)
        unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        countable_income = countable_earned + unearned
        need_standard = spm_unit("ne_adc_need_standard", period)
        return countable_income < need_standard
