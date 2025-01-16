from policyengine_us.model_api import *


class pr_low_income_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible unit for the Puerto Rico low income credit"
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30212-credit-for-low-income-individuals-older-than-sixty-five-65-years-of-age"
    defined_for = "pr_low_income_credit_eligible_people"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.low_income
        eligible_people = tax_unit(
            "pr_low_income_credit_eligible_people", period
        )
        income = tax_unit("pr_gross_income", period)
        income_limit = p.income_limit.calc(eligible_people)
        return income <= income_limit
