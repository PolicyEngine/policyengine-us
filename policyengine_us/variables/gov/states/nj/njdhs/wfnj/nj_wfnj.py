from policyengine_us.model_api import *


class nj_wfnj(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey WFNJ benefit"
    unit = USD
    definition_period = MONTH
    defined_for = "nj_wfnj_eligible"
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-3"
    )

    def formula(spm_unit, period, parameters):
        payment_levels = spm_unit("nj_wfnj_payment_levels", period)
        countable_income = spm_unit("nj_wfnj_countable_income", period)
        return max_(payment_levels - countable_income, 0)
