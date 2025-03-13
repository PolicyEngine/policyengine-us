from policyengine_us.model_api import *


class pr_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1005-computation-of-taxable-income/subchapter-a-determination-of-net-income-general-concepts/30101-gross-income"
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income # gross_income/sources
        income = 0
        for source in p.gross_income.sources:
            # if the source has over 0 income, add it to total
            income += max_0(0, add(tax_unit, period, [source])) 
        return income
