from policyengine_us.model_api import *

class pr_compensatory_low_income_credit(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Additional compensatory low income credit"
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30212-credit-for-low-income-individuals-older-than-sixty-five-65-years-of-age"
    defined_for = "pr_compensatory_low_income_credit_eligible"

    adds = "gov.territories.pr.tax.income.credits.low_income.additional.amount"
