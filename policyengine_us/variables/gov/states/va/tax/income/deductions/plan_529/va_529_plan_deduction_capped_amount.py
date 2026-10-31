from policyengine_us.model_api import *


class va_529_plan_deduction_capped_amount(Variable):
    value_type = float
    entity = Person
    label = "Virginia Commonwealth Savers deduction within the per-account cap"
    documentation = (
        "Sum, across the Commonwealth Savers accounts this person owns, of the "
        "lesser of the per-account cap or the account's contributions for the "
        "year plus its undeducted carryforward. Supply it from account records; "
        "otherwise it is computed as if contributions and carryforwards were "
        "split evenly across count_529_contribution_beneficiaries accounts."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # Va. Code § 58.1-322.03(7)(a)
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-322.03/",
        # 2024 Form 760 instructions, deduction code 104
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2024-760-instructions.pdf#page=28",
    )
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.plan_529
        # § 58.1-322.03(7)(a) caps each contract or account separately, so the
        # exact amount needs account-level records. Total contributions and
        # an account count only bound it: with an even split, each of n
        # accounts holds 1/n of the total, giving min(total, cap x n), the
        # largest deduction any split of the same total allows.
        contributions = person("investment_in_529_plan_indv", period)
        carryforward = person("va_529_plan_carryforward", period)
        accounts = person("count_529_contribution_beneficiaries", period)
        return min_(contributions + carryforward, p.cap * accounts)
