from policyengine_us.model_api import *


class la_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Louisiana TANF income eligible"
    definition_period = MONTH
    reference = "https://ldh.la.gov/page/fitap"
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        # Per FITAP rules: countable income cannot exceed the flat grant
        countable_income = spm_unit("la_tanf_countable_income", period)
        flat_grant = spm_unit("la_tanf_flat_grant", period)
        return countable_income <= flat_grant
