from policyengine_us.model_api import *


class foreign_earned_income_exclusion_disallowed_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Foreign income deductions disallowed on the federal tax worksheet"
    unit = USD
    documentation = "Itemized deductions or exclusions disallowed because they relate to excluded foreign income: Foreign Earned Income Tax Worksheet line 2b. This adjustment is separate from Form 2555 line 44 and reduces the federal stacking amount, not Form 2555 line 43. This input only supplies the federal rate worksheet adjustment; other income and deduction inputs retain their existing model definitions."
    definition_period = YEAR
    reference = [
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=37",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
    ]
