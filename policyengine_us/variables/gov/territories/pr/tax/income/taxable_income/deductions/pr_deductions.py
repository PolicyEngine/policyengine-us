from policyengine_us.model_api import *


class pr_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico deductions"
    unit = USD
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/"
    definition_period = YEAR
    defined_for = StateCode.PR

    adds = "gov.territories.pr.tax.income.taxable_income.deductions.sources"
