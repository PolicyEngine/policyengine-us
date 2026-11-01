from policyengine_us.model_api import *


class pr_low_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico low income credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1007/subchapter-b/30212/"
    defined_for = "pr_low_income_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.low_income.amount
        eligible_people = tax_unit("pr_low_income_credit_eligible_people", period)
        return p.base * eligible_people
