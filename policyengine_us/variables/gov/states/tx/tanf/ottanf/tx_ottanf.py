from policyengine_us.model_api import *


class tx_ottanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas One-Time TANF (OTTANF) payment"
    unit = USD
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2410-general-policy"
    defined_for = "tx_ottanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tanf.ottanf

        # One-time payment of $1,000 divided by 12 for monthly equivalent
        return p.payment_amount / MONTHS_IN_YEAR
