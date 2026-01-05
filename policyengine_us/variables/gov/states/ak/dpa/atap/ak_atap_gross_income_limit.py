from policyengine_us.model_api import *


class ak_atap_gross_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP gross income limit"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.520"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Per 7 AAC 45.520: Gross income limit is 185% of need standard
        p = parameters(period).gov.states.ak.dpa.atap
        need_standard = spm_unit("ak_atap_need_standard", period)
        return need_standard * p.gross_income_limit_rate
