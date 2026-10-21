from policyengine_us.model_api import *


class hi_ccap_tanf_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF payments counted as Hawaii CCAP income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = (
        # HAR 17-798.3-10(b)(11), eff. 2021-08-06.
        "https://www.law.cornell.edu/regulations/hawaii/Haw-Code-R-SS-17-798-3-10",
    )

    def formula(spm_unit, period, parameters):
        # HAR 17-798.3-10(b)(11) counts "Hawaii public assistance payments
        # prior to any reduction of the monthly assistance payment due to
        # overpayment recovery". The model has no overpayment recovery, so
        # the payment is the Hawaii TANF grant the family takes up.
        # Reading tanf here would be circular: tanf sums every state's TANF
        # program, several of which deduct childcare_expenses, which nets
        # out child_care_subsidies, which includes Hawaii CCAP. hi_tanf under
        # the TANF take-up gate equals tanf for Hawaii households.
        if parameters(period).gov.hhs.tanf.abolish_tanf:
            return 0
        takes_up = spm_unit("takes_up_tanf_if_eligible", period.this_year)
        return spm_unit("hi_tanf", period) * takes_up
