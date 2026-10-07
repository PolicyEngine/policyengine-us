from policyengine_us.model_api import *


class medicaid_ltss_impairment_related_work_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS qualifying impairment-related work expenses"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Expenses paid by this person for items or services necessary to "
        "work because of an impairment, qualifying under 20 CFR 416.976. "
        "Report reasonable costs not paid or reimbursable by another "
        "source, allocated to the month "
        "under that section's payment and allocation rules, excluding "
        "amounts already deducted as business expenses. This input "
        "describes the qualifying costs; the model separately derives "
        "the disability, blindness, and age conditions and applies the "
        "exclusion in the income-budget sequence. Each spouse reports "
        "their own expenses."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78#page=6",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-1112.htm",
    )
