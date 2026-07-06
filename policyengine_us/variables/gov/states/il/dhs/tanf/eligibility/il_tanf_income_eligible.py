from policyengine_us.model_api import *


class il_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Illinois Temporary Assistance for Needy Families (TANF) due to income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.155",
        # IDHS PM 10-01-02 Minimum Payment (WAG 10-01-02):
        # "A family qualifies for TANF benefits, if nonexempt income is at
        #  least $1 less than the Payment Level for the unit's size."
        # "If nonexempt income is equal to or greater than the Payment Level,
        #  eligibility for cash benefits under the TANF program does not exist."
        "https://www.dhs.state.il.us/page.aspx?item=15820",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit(
            "il_tanf_countable_income_for_initial_eligibility", period
        )
        payment_level = spm_unit(
            "il_tanf_payment_level_for_initial_eligibility", period
        )
        # Nonexempt income must be at least the minimum payment ($1) below the
        # payment level; income equal to or above the payment level is
        # ineligible.
        minimum_payment = parameters(period).gov.states.il.dhs.tanf.minimum_payment
        return (payment_level - countable_income) >= minimum_payment
