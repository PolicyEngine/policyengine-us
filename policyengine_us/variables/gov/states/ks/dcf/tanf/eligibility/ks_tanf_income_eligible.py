from policyengine_us.model_api import *


class ks_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Kansas TANF income eligibility"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-110",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm7110.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per K.A.R. 30-4-110 and KEESM 7110:
        # Countable income must be less than the payment standard
        countable_income = spm_unit("ks_tanf_countable_income", period)
        payment_standard = spm_unit("ks_tanf_maximum_benefit", period)
        return countable_income < payment_standard
