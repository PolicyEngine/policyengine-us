from policyengine_us.model_api import *


class adjusted_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico Adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30103/"

    def formula(tax_unit, period, parameters):
        gross_income = add(tax_unit, period, ["pr_gross_income"])
        exemptions = tax_unit("exemptions", period)
        above_line_deductions = tax_unit("above_the_line_deductions", period)
        
        return max_(0, gross_income - exemptions - above_line_deductions) 
