from policyengine_us.model_api import *


class pr_compensatory_low_income_credit(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Additional compensatory low income credit"
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1007/subchapter-b/30212/"
    defined_for = "pr_low_income_credit_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.low_income.amount
        pension_income = person("pension_income", period)
        return p.additional.calc(pension_income, right=True)
