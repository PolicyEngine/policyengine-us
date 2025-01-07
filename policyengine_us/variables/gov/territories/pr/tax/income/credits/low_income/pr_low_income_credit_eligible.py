from policyengine_us.model_api import *


class pr_low_income_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible unit for the Puerto Rico low income credit"
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30212-credit-for-low-income-individuals-older-than-sixty-five-65-years-of-age"
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.low_income.income_limit
        eligible_person = tax_unit.members("pr_low_income_credit_eligible_person", period)
        eligible_people = tax_unit.sum(eligible_person)
        income = tax_unit("pr_gross_income", period)
        income_limit = select(
            [
                eligible_people == 1,
                eligible_people == 2,
            ],
            [
                p.one_eligible_person,
                p.two_eligible_people,
            ],
            default = 0
        )
        return where(eligible_people > 0, income <= income_limit, False)
