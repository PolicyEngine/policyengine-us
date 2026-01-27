from policyengine_us.model_api import *


class la_fitap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Louisiana FITAP income eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/louisiana/La-Admin-Code-tit-67-SS-III-1229"
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        # Per LAC 67:III.1229.E: Countable income cannot exceed flat grant
        countable_income = spm_unit("la_fitap_countable_income", period)
        flat_grant = spm_unit("la_fitap_flat_grant", period)
        return countable_income <= flat_grant
