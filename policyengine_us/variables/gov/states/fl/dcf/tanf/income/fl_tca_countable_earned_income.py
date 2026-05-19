from policyengine_us.model_api import *


class fl_tca_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TCA countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html"
    defined_for = StateCode.FL

    def formula(spm_unit, period, parameters):
        # Per DCF 2620.0111.01: Income Test and Benefit Determination
        # Step 2: Subtract $90 standard disregard
        # Step 3: Subtract $200 and 1/2 of remainder
        p = parameters(period).gov.states.fl.dcf.tanf.income.disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Step 2: Subtract $90 standard disregard
        after_standard = max_(gross_earned - p.standard_disregard, 0)

        # Step 3: Subtract $200, then 50% of remainder is countable
        remaining_after_first = max_(after_standard - p.first_amount, 0)
        return remaining_after_first * (1 - p.remaining_rate)
