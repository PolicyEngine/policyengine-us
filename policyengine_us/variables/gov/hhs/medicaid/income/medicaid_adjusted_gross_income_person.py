from policyengine_us.model_api import *


class medicaid_adjusted_gross_income_person(Variable):
    value_type = float
    entity = Person
    label = "Federal adjusted gross income for Medicaid MAGI household rules"
    unit = USD
    documentation = (
        "Each person's AGI for Medicaid MAGI-based income: their own gross "
        "income less their own above-the-line deductions "
        "(above_the_line_deductions_person). On a joint return a deduction "
        "that belongs to one spouse, such as their IRA deduction or business "
        "loss, lowers only that spouse's amount, and the head's and spouse's "
        "amounts add up to the return's AGI. A tax unit dependent's amount is "
        "the AGI of the dependent's own return: their own income less their "
        "own deductions, alimony paid included. It can be negative; "
        "medicaid_household_income floors the household's total, not each "
        "person's amount."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/62",
        "https://www.law.cornell.edu/cfr/text/42/435.603#e",
    )

    def formula(person, period, parameters):
        gross_income = person("medicaid_irs_gross_income", period)
        deductions = person("above_the_line_deductions_person", period)
        agi = gross_income - deductions

        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            basic_income = person.tax_unit("basic_income", period)
            # Divided equally between the head and spouse, as in
            # adjusted_gross_income_person.
            agi += basic_income * filer_share(person, period, 0 * basic_income)

        return agi
