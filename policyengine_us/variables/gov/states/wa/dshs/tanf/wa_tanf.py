from policyengine_us.model_api import *


class wa_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-478-0020",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0165",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Get parameters
        p = parameters(period).gov.states.wa.dshs.tanf.benefit

        # Check eligibility
        eligible = spm_unit("wa_tanf_eligible", period)

        # Get payment standard
        payment_standard = spm_unit("wa_tanf_payment_standard", period)

        # Get countable income
        countable_income = spm_unit("wa_tanf_countable_income", period)

        # Calculate grant amount: Payment Standard - Countable Income
        grant_before_cap = max_(payment_standard - countable_income, 0)

        # Apply maximum grant cap
        grant_with_cap = min_(grant_before_cap, p.maximum_grant_cap)

        # Return grant if eligible, otherwise 0
        return where(eligible, grant_with_cap, 0)
