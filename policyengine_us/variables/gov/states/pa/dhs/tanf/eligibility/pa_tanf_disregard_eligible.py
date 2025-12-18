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

        is_enrolled = spm_unit("is_tanf_enrolled", period)

        gross_earned = person("tanf_gross_earned_income", period)
        preliminary_earned_per_person = max_(
            gross_earned - p.work_expense.initial, 0
        )
        preliminary_earned = spm_unit.sum(preliminary_earned_per_person)

        preliminary_unearned = add(
            spm_unit, period, ["tanf_gross_unearned_income"]
        )

        preliminary_income = preliminary_earned + preliminary_unearned
        standard_of_need = spm_unit("pa_tanf_standard_of_need", period)

        return is_enrolled | (preliminary_income < standard_of_need)
