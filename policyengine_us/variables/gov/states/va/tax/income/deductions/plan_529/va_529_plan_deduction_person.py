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
        # § 58.1-322.03(7)(a): up to $4,000 per contract or account each year,
        # with any excess carried forward until fully deducted.
        capped = person("va_529_plan_deduction_capped_amount", period)
        # § 58.1-322.03(7)(b): an owner who has attained age 70 deducts the
        # full amount contributed, less any amounts previously deducted, so
        # this year's contributions and the undeducted carryforward.
        contributions = person("investment_in_529_plan_indv", period)
        carryforward = person("va_529_plan_carryforward", period)
        age_exempt = person("age", period) >= p.age_threshold
        return head_or_spouse * where(age_exempt, contributions + carryforward, capped)
