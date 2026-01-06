from policyengine_us.model_api import *


class la_fitap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Louisiana FITAP"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/louisiana/La-Admin-Code-tit-67-SS-III-1229"
    defined_for = "la_fitap_eligible"

    def formula(spm_unit, period, parameters):
        flat_grant = spm_unit("la_fitap_flat_grant", period)
        countable_income = spm_unit("la_fitap_countable_income", period)

        # Benefit = flat grant minus countable income
        return max_(flat_grant - countable_income, 0)
