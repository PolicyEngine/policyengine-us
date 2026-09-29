from policyengine_us.model_api import *


class self_employment_expense(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Self-employment business expenses"
    documentation = (
        "Business expenses, other than cost of goods sold, deducted in arriving "
        "at the person's reported net self-employment income, combined across "
        "the person's farm and non-farm sole proprietorships: Schedule C line "
        "28 total expenses plus line 30 business use of the home, and Schedule "
        "F line 33 total expenses. Exclude cost of goods sold (Schedule C line "
        "4; Schedule F line 1b, or Part III line 49 for accrual-method farms), "
        "so that net profit plus this input equals Schedule C line 7 and "
        "Schedule F line 9 gross income. Exclude employee work-related "
        "expenses and personal income and self-employment taxes. Treated as "
        "zero when not reported."
    )
    reference = (
        "https://www.irs.gov/instructions/i1040sc",
        "https://www.irs.gov/instructions/i1040sf",
        "https://www.irs.gov/pub/irs-pdf/f1040sc.pdf#page=1",
        "https://www.irs.gov/pub/irs-pdf/f1040sf.pdf#page=1",
    )
