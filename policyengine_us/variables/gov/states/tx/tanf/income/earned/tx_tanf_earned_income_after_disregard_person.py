from policyengine_us.model_api import *


class tx_tanf_earned_income_after_disregard_person(Variable):
    value_type = float
    entity = Person
    label = "Texas TANF earned income after disregards (person)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1420-types-deductions",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-409",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        # Get gross earned income
        gross_earned = person("tx_tanf_gross_earned_income", period)
        p = parameters(period).gov.states.tx.tanf.income

        # Step 1: Subtract work expense deduction ($120, not to exceed earnings)
        work_expense = min_(p.deductions.work_expense, gross_earned)
        after_work_expense = max_(gross_earned - work_expense, 0)

        # Step 2: Apply appropriate earned income disregard
        # Check if household is enrolled in TANF
        spm_unit = person.spm_unit
        is_enrolled = spm_unit("is_tanf_enrolled", period)

        # For applicants (not enrolled): 1/3 disregard
        applicant_disregard = (
            after_work_expense * p.disregards.applicant_fraction
        )

        # For continuing recipients (enrolled): 90% disregard (capped at $1,400)
        # Note: This disregard is limited to 4 months per 12-month period (not yet implemented)
        potential_recipient_disregard = (
            after_work_expense * p.disregards.continuing_recipient_rate
        )
        actual_recipient_disregard = min_(
            potential_recipient_disregard,
            p.disregards.continuing_recipient_cap,
        )

        # Return appropriate value based on enrollment status
        disregard = where(
            is_enrolled,
            actual_recipient_disregard,
            applicant_disregard,
        )

        return max_(after_work_expense - disregard, 0)
