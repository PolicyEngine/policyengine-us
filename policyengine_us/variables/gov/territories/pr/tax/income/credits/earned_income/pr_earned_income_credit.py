from policyengine_us.model_api import *


class pr_earned_income_credit(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico earned income credit amount"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30211-earned-income-credit"
    defined_for = "pr_earned_income_credit_eligible"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.earned_income

        gross_income = person("pr_gross_income_person", period)
        # if in the lower bracket: gross_income * rate. if higher, use max credit
        phase_in = min_(gross_income * p.phase_in_rate, p.max_amount)
        phase_out = p.phase_out_rate.calc(gross_income)

        return phase_in - phase_out
