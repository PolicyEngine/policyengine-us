from policyengine_us.model_api import *


class pr_retirement_deduction(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico retirement contribution deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/"  # (7)
    defined_for = "pr_retirement_deduction_eligibility"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.retirement

        agi = person("pr_agi_person", period)
        max_deduction = min_(p.max, agi)
        contributions = add(
            person,
            period,
            ["traditional_ira_contributions", "roth_ira_contributions"],
        )
        return min_(max_deduction, contributions)
