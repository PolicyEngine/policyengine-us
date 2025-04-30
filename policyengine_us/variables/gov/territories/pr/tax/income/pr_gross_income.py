from policyengine_us.model_api import *


class pr_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30101/"

    adds = "gov.territories.pr.tax.income.gross_income.sources"
