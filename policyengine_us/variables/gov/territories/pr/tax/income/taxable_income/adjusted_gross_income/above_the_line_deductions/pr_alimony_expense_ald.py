from policyengine_us.model_api import *


class pr_alimony_expense_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico Alimony expense Above-the-line deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30133/"

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["alimony_expense"])
