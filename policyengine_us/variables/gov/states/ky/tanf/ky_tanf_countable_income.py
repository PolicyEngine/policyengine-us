from policyengine_us.model_api import *


class ky_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky Transitional Assistance Program countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        earned = spm_unit("ky_tanf_countable_earned_income", period)
        unearned = spm_unit("ky_tanf_countable_unearned_income", period)
        return earned + unearned
