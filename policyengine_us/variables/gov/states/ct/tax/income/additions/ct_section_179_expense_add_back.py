from policyengine_us.model_api import *


class ct_section_179_expense_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Section 179 Expense Add Back"
    definition_period = YEAR
    documentation = "Add 80 percent of the section 179 amount deducted in determining federal AGI."
    reference = "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/2022-CT-1040-Instructions_1222.pdf#page=7"
    # use federal variables if they are added later
