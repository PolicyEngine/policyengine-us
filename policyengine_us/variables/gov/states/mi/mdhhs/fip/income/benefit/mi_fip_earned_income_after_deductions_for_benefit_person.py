from policyengine_us.model_api import *


class mi_fip_earned_income_after_deductions_for_benefit_person(Variable):
    value_type = float
    entity = Person
    label = (
        "Michigan FIP earned income after deductions for benefit per person"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf#page=5",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf#page=4",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mi.mdhhs.fip.income.disregard

        # Get gross earned income for this person
        gross_earned = person("tanf_gross_earned_income", period)

        # BEM 518 Page 5 - "Issuance Earned Income Disregard"
        # BEM 520 Section D - Issuance Test (for benefit calculation)
        # "Deduct $200 from each person's countable earnings. Then deduct an
        # additional 50 percent of each person's remaining earnings."

        # This is used for BENEFIT CALCULATION for ALL recipients
        # (both new applicants and enrolled recipients use 50% for benefits)

        # Step 1: Deduct $200 from this person's earnings
        flat_deduction = p.flat
        remainder = max_(gross_earned - flat_deduction, 0)

        # Step 2: Deduct 50% of remainder (for benefit calculation)
        percent_deduction = remainder * p.ongoing_rate

        # Step 3: Countable income (cannot be negative)
        # "The total disregard cannot exceed countable earnings" - BEM 518
        return max_(gross_earned - flat_deduction - percent_deduction, 0)
