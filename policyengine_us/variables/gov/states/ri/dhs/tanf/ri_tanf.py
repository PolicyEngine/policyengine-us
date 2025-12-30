from policyengine_us.model_api import *


class ri_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island TANF benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
        "https://dhs.ri.gov/programs-and-services/ri-works-program",
    )
    defined_for = "ri_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.tanf
        payment_standard = spm_unit("ri_tanf_payment_standard", period)
        countable_income = spm_unit("ri_tanf_countable_income", period)

        # Benefit = Payment Standard - Countable Income
        benefit = max_(payment_standard - countable_income, 0)

        # Per 218-RICR-20-00-2: No payment if amount < $10
        return where(benefit >= p.minimum_benefit, benefit, 0)
