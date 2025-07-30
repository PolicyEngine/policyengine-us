from policyengine_us.model_api import *


class pr_retirement_deduction_eligibility(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico retirement contribution deduction eligibility"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/"  # (7)(D)
    defined_for = StateCode.PR

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.retirement

        # additionally no deduction if income is only from pension and annuities
        age = person("age", period)
        return age < p.age_threshold
