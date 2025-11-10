from policyengine_us.model_api import *


class pa_tanf_earned_income_after_deductions_person(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania TANF earned income after deductions per person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = (
        "http://services.dpw.state.pa.us/oimpolicymanuals/cash/160_Income_Deductions/160_2_TANF_Earned_Income_Deductions.htm",
        "https://www.law.cornell.edu/regulations/pennsylvania/55-Pa-Code-SS-183-94",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf.income.deductions

        # Get gross earned income for this person
        gross_earned = person("tanf_gross_earned_income", period)

        # Check if eligible for Earned Income Disregard (EID)
        # Eligibility determined by pa_tanf_disregard_eligible:
        # - Enrolled recipients: automatic
        # - New applicants: must pass Standard of Need test (using $90 deduction)
        disregard_eligible = person.spm_unit(
            "pa_tanf_disregard_eligible", period
        )

        # Per PA DHS Cash Assistance Handbook Section 160.22:
        # "If the individual is eligible for the EID, calculate and subtract the EID
        # and subsequently subtract the $200 WED."
        # "If an individual is not eligible for the EID, the CAO will not deduct the WED."

        # Step 1: Apply 50% Earned Income Disregard (EID) to GROSS earned income
        # "Disregard 50%" = keep only 50%
        disregard_percentage = p.earned_income_disregard.percentage
        keep_rate = 1 - disregard_percentage
        after_eid = gross_earned * keep_rate

        # Step 2: Subtract $200 Work Expense Deduction (WED)
        # Only applied if eligible for EID
        after_wed = max_(after_eid - p.work_expense.additional, 0)

        # Return countable income based on eligibility
        return where(
            disregard_eligible,
            # Eligible: apply EID + WED
            after_wed,
            # Not eligible: full earned income is countable (no deductions)
            gross_earned,
        )
