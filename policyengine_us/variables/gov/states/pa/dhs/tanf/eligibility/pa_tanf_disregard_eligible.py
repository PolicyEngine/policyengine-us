from policyengine_us.model_api import *


class pa_tanf_disregard_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF earned income disregard eligibility"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.law.cornell.edu/regulations/pennsylvania/55-Pa-Code-SS-183-94"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(period).gov.states.pa.dhs.tanf.income.deductions

        # Continuing recipients automatically eligible (enrolled OR received TANF in last 4 months)
        # Simplified: use is_tanf_enrolled as proxy for recent receipt
        is_enrolled = spm_unit("is_tanf_enrolled", period)

        # New applicants must pass Standard of Need test:
        # Calculate preliminary income after standard deductions
        # 1. Earned income after $90 deduction per person
        gross_earned = person("tanf_gross_earned_income", period)
        preliminary_earned_per_person = max_(
            gross_earned - p.work_expense.initial, 0
        )
        preliminary_earned = spm_unit.sum(preliminary_earned_per_person)

        # 2. Unearned income (no deductions in simplified version)
        gross_unearned = person("tanf_gross_unearned_income", period)
        preliminary_unearned = spm_unit.sum(gross_unearned)

        # 3. Total preliminary income
        preliminary_income = preliminary_earned + preliminary_unearned

        # 4. Compare to Standard of Need
        standard_of_need = spm_unit("pa_tanf_standard_of_need", period)
        passes_test = preliminary_income < standard_of_need

        # Eligible if enrolled OR passes test
        return is_enrolled | passes_test
