from policyengine_us.model_api import *


class vt_reach_up(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://legislature.vermont.gov/statutes/fullchapter/33/011",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = "vt_reach_up_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("vt_reach_up_payment_standard", period)
        countable_income = spm_unit("vt_reach_up_countable_income", period)
        benefit = max_(payment_standard - countable_income, 0)
        return min_(benefit, payment_standard)
