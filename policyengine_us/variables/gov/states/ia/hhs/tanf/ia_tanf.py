from policyengine_us.model_api import *


class ia_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa Family Investment Program"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27",
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28",
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-45-27",
    )
    defined_for = "ia_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("ia_tanf_payment_standard", period)
        countable_income = spm_unit("ia_tanf_countable_income", period)
        # Per IAC 441-45.27: round down to whole dollar
        return np.floor(max_(payment_standard - countable_income, 0))
