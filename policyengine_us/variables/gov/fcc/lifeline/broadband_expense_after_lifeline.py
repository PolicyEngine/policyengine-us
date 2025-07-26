from policyengine_us.model_api import *


class broadband_expense_after_lifeline(Variable):
    value_type = float
    entity = SPMUnit
    label = "Broadband expense after Lifeline"
    documentation = "Broadband expense after Lifeline benefits"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/cfr/text/47/54.403"

    def formula(spm_unit, period, parameters):
        broadband = spm_unit("broadband_expense", period)
        lifeline = spm_unit("lifeline", period)
        return max_(broadband - lifeline, 0)
