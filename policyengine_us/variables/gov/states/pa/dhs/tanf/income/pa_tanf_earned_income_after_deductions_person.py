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
        after_initial = max_(gross_earned - p.initial_work_expense.amount, 0)

        # Step 2: Apply 50% earned income disregard (only if eligible)
        # Eligibility: enrolled OR received TANF in 1 of last 4 months
        # Simplified: use is_tanf_enrolled as proxy
        is_enrolled = person.spm_unit("is_tanf_enrolled", period)

        # Apply disregard conditionally
        # "Disregard 50%" = keep only 50%, so multiply by (1 - 0.5)
        after_disregard = where(
            is_enrolled,
            # Recipients: apply 50% disregard (keep 50% of remaining)
            after_initial * (1 - p.earned_income_disregard.percentage),
            # New applicants: no disregard (keep 100%)
            after_initial,
        )

        # Step 3: Subtract $200 additional work expense deduction (everyone)
        countable = max_(after_disregard - p.additional_work_expense.amount, 0)

        return countable
