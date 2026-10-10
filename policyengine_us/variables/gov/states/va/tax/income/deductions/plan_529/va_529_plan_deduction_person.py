from policyengine_us.model_api import *


class va_529_plan_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia Commonwealth Savers account deduction claimed by each owner"
    unit = USD
    definition_period = YEAR
    reference = (
        # Va. Code § 58.1-322.03(7)(a)-(b)
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-322.03/",
        # 2024 Form 760 instructions, deduction code 104
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2024-760-instructions.pdf#page=28",
    )
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.plan_529
        # Only the owner of record of an account may claim the deduction, so
        # each filer deducts the contributions to accounts they own; the model
        # reads a person's 529 contributions as contributions to their own
        # accounts. Dependents file their own returns, which this tax unit
        # does not model, so dependent-owned accounts are excluded.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        contributions = person("investment_in_529_plan_indv", period)
        accounts = person("count_529_contribution_beneficiaries", period)
        capped = min_(contributions, p.cap * accounts)
        # An owner who has attained age 70 may deduct the full amount
        # contributed during the year.
        age_exempt = person("age", period) >= p.age_threshold
        return head_or_spouse * where(age_exempt, contributions, capped)
