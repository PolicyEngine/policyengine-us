from policyengine_us.model_api import *


class pr_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1004/subchapter-a/30061/"
