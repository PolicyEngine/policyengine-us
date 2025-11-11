from policyengine_us.model_api import *


class mi_fip_earned_income_after_deductions_person(Variable):
    value_type = float
    entity = Person
    label = "Michigan FIP earned income after deductions per person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.mdhhs.fip.income.deductions.earned_income_disregard

        # Get gross earned income for this person
        gross_earned = person("tanf_gross_earned_income", period)

        # Check enrollment status to determine which rate to use
        enrolled = person.spm_unit("is_tanf_enrolled", period)

        # BEM 518 Page 5:
        # Qualifying (Initial): "deduct $200... Then deduct an additional 20 percent"
        # Issuance (Ongoing): "Deduct $200... Then deduct an additional 50 percent"

        # Step 1: Deduct $200 from each person's earnings
        flat_deduction = p.flat_amount
        remainder = max_(gross_earned - flat_deduction, 0)

        # Step 2: Apply percentage based on enrollment status
        # BEM 520 Section C (Qualifying): "Enter 20 percent of the total in line 5"
        # BEM 520 Section D (Issuance): "Enter 50 percent of the total in line 5"
        percent_deduction = where(
            enrolled,
            remainder * p.ongoing_percent,  # 50% for enrolled (since 2011)
            remainder * p.initial_percent,  # 20% for new applicants
        )

        # Step 3: Total deduction
        total_deduction = flat_deduction + percent_deduction

        # Step 4: Countable income (cannot be negative)
        # "The total disregard cannot exceed countable earnings" - BEM 518
        return max_(gross_earned - total_deduction, 0)
