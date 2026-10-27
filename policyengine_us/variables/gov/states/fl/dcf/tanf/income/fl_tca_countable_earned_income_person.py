from policyengine_us.model_api import *


class fl_tca_countable_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = "Florida TCA countable earned income per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://ffic.myflfamilies.com/manual/2400.pdf#page=27",
        "https://ffic.myflfamilies.com/manual/2400.pdf#page=28",
        "https://ffic.myflfamilies.com/manual/2600.pdf#page=21",
    )
    defined_for = StateCode.FL

    def formula(person, period, parameters):
        # Per DCF 2420.0304, "The first $90 of each individual's gross earned
        # income is deducted in a regular budget", and per 2420.0314 the
        # $200 and 1/2 disregard applies to "a portion of the individual's
        # remaining earned income following the standard earned income
        # deduction". Both disregards are applied to each earner.
        p = parameters(period).gov.states.fl.dcf.tanf.income.disregard
        gross_earned = person("tanf_gross_earned_income", period)

        # 2620.0111.01 Step 2: subtract the $90 standard disregard (always).
        after_standard = max_(gross_earned - p.standard_disregard, 0)

        # 2620.0111.01 Step 3: subtract the remainder of the $200 and 1/2
        # disregard "if eligible" (2420.0314-.0315). Eligibility is tested for
        # the unit.
        eligible = person.spm_unit("fl_tca_200_and_half_disregard_eligible", period)
        # Per 2420.0315, the $90 standard disregard "is included in the first
        # $200 earned income disregard", so only the remaining $110 is
        # subtracted here, "for a total of $200".
        remainder_of_first_amount = p.first_amount - p.standard_disregard
        remaining_after_first = max_(after_standard - remainder_of_first_amount, 0)
        countable_with_full_disregard = remaining_after_first * (1 - p.remaining_rate)
        return where(eligible, countable_with_full_disregard, after_standard)
