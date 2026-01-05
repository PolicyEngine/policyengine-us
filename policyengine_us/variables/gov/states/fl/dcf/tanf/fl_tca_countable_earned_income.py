from policyengine_us.model_api import *


class fl_tca_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TCA countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://flrules.org/gateway/RuleNo.asp?id=65A-4.210",
    )
    defined_for = StateCode.FL

    def formula(spm_unit, period, parameters):
        # Per Florida Statutes 414.095(11): First $200 plus 50% of remainder
        p = parameters(period).gov.states.fl.dcf.tanf.income.disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Calculate disregard: $200 + 50% of (gross - $200)
        first_amount = p.first_amount
        remaining_after_first = max_(gross_earned - first_amount, 0)
        disregard = first_amount + remaining_after_first * p.remaining_rate

        return max_(gross_earned - disregard, 0)
