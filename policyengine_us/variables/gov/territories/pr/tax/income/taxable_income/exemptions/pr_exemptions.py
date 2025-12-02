from policyengine_us.model_api import *


class pr_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico exemptions"
    definition_period = YEAR
    unit = USD
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30138/"
    defined_for = StateCode.PR

    adds = "gov.territories.pr.tax.income.taxable_income.exemptions.sources"
