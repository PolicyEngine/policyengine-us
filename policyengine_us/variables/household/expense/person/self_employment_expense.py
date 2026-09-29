from policyengine_us.model_api import *


class self_employment_expense(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Self-employment business expenses"
    documentation = (
        "Business expenses already deducted from regular, SSTB, and farm net "
        "self-employment income, excluding cost of goods sold: tax year 2025 "
        "Schedule C lines 28 and 30, and Schedule F line 33. Excludes employee "
        "work expenses and personal income and self-employment taxes. Defaults "
        "to zero when not reported. Used to reconstruct gross income, not to "
        "reduce reported net income again or determine program-allowable costs."
    )
    reference = (
        "https://www.irs.gov/pub/irs-prior/f1040sc--2025.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/f1040sf--2025.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/f1040sf--2025.pdf#page=2",
    )
