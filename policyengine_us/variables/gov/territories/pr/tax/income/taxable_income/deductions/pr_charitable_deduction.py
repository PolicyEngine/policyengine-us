from policyengine_us.model_api import *


class pr_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico charitable deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/"  # (3)(B)(i)(IV)
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.charity
        charitable_contributions = add(
            tax_unit,
            period,
            ["charitable_cash_donations", "charitable_non_cash_donations"],
        )
        charity_floor = p.floor * tax_unit("pr_agi", period)
        return min_(charitable_contributions, charity_floor)
