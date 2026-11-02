from policyengine_us.model_api import *


class wv_lieap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "West Virginia LIEAP income eligible"
    definition_period = YEAR
    defined_for = StateCode.WV
    reference = (
        # PDF pages 1725,1749
        "https://bfa.wv.gov/media/39948/download?inline=#page=1725",
        # PDF pages 1726,1752
        "https://bfa.wv.gov/media/40005/download?inline=#page=1726",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("wv_lieap_household_size", period)
        income = spm_unit("wv_lieap_countable_income", period)
        limit = spm_unit("wv_lieap_income_limit", period)
        return (size > 0) & (income <= limit)
