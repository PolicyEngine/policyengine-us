from policyengine_us.model_api import *


class ia_tanf_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa TANF gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"

    def formula(spm_unit, period, parameters):
        earned = spm_unit("ia_tanf_gross_earned_income", period)
        unearned = spm_unit("ia_tanf_gross_unearned_income", period)
        return earned + unearned
