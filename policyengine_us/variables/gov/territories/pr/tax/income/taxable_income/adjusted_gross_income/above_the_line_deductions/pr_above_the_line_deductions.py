from policyengine_us.model_api import *


class pr_above_the_line_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico Above-the-line deductions"
    unit = USD
    documentation = (
        "Deductions applied to reach adjusted gross income from gross income."
    )
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30103/"

    # adds function over specific deductions listed to calculate agi
    # source list is a parameter, have specific deductions as variables in this folder
    adds = "gov.territories.pr.tax.income.taxable_income.ald.deductions"
