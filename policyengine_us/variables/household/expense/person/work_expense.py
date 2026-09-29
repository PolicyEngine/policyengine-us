from policyengine_us.model_api import *


class work_expense(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Self-employment work expenses"
    documentation = (
        "Self-employment business costs already deducted in arriving at the "
        "reported net self-employment income, combined across all of the "
        "person's farm and non-farm businesses. Include every cost deducted on "
        "Schedule C (Part II expenses, the line 30 business use of home, and "
        "Part III cost of goods sold) and on Schedule F (Part II expenses and "
        "the line 1b cost or other basis of resale items), so that net income "
        "plus this input equals gross receipts. Exclude employee work-related "
        "expenses such as commuting, uniforms, and tools, and exclude personal "
        "income and self-employment taxes. Treated as zero when not reported."
    )
