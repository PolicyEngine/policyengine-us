from openfisca_us.model_api import *


class md_qualified_tuition_expense_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD qualified tuition expenses addition to agi"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-2/part-ii/section-10-204/"
    """
     (h)    The addition under subsection (a) of this section includes the amount deducted under § 222 of the Internal Revenue Code for qualified tuition and related expenses paid during the taxable year.
    """

    formula = sum_of_variables(["qualified_tuition_expenses"])
