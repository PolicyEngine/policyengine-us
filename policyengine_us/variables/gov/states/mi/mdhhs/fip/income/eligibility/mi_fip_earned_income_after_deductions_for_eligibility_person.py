from policyengine_us.model_api import *


class mi_fip_earned_income_after_deductions_for_eligibility_person(Variable):
    value_type = float
    entity = Person
    label = "Michigan FIP earned income after deductions for eligibility per person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mi.mdhhs.fip.income.disregard

        # Get gross earned income for this person
        gross_earned = person("tanf_gross_earned_income", period)

        # BEM 518 Page 5 - "Qualifying Earned Income Disregard"
        # BEM 520 Section C - Qualifying Income Test (for initial eligibility)
        # "At application, deduct $200 from each person's countable earnings.
        # Then deduct an additional 20 percent of each person's remaining earnings."

        # Step 1: Deduct $200 from this person's earnings
        flat_deduction = p.flat
        remainder = max_(gross_earned - flat_deduction, 0)

        # Step 2: Deduct 20% of remainder (for initial eligibility test)
        percent_deduction = remainder * p.initial_rate

        # Step 3: Total deduction
        total_deduction = flat_deduction + percent_deduction

        # Step 4: Countable income (cannot be negative)
        return max_(gross_earned - total_deduction, 0)
