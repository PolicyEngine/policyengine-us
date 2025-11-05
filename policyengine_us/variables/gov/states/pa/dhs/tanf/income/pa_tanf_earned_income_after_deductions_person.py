from policyengine_us.model_api import *


class pa_tanf_earned_income_after_deductions_person(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania TANF earned income after deductions per person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.law.cornell.edu/regulations/pennsylvania/55-Pa-Code-SS-183-94"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf.income.deductions

        # Get gross earned income for this person
        gross_earned = person("tanf_gross_earned_income", period)

        # Step 1: Subtract $90 initial work expense deduction (everyone)
        after_initial = max_(gross_earned - p.work_expense.initial, 0)

        # Step 2: Apply 50% earned income disregard (only if eligible)
        # Eligibility determined by pa_tanf_disregard_eligible:
        # - Enrolled recipients: automatic
        # - New applicants: must pass Standard of Need test
        disregard_eligible = person.spm_unit(
            "pa_tanf_disregard_eligible", period
        )

        # Apply disregard conditionally
        # "Disregard 50%" = keep only 50%
        disregard_percentage = p.earned_income_disregard.percentage
        keep_rate = 1 - disregard_percentage

        after_disregard = where(
            disregard_eligible,
            # Eligible: apply 50% disregard (keep 50% of remaining)
            after_initial * keep_rate,
            # Not eligible: no disregard (keep 100%)
            after_initial,
        )

        # Step 3: Subtract $200 additional work expense deduction (everyone)
        return max_(after_disregard - p.work_expense.additional, 0)
