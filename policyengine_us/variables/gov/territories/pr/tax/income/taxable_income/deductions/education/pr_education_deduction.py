from policyengine_us.model_api import *


class pr_education_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico education contribution deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/"  # (8)
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.education
        contributions = add(tax_unit, period, ["investment_in_529_plan"])
        count = tax_unit("pr_education_deduction_beneficiary_count", period)
        maximum_contribution = p.max * count
        return min_(maximum_contribution, contributions)
