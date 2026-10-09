from policyengine_us.model_api import *


class foreign_earned_income_exclusion_allocable_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Deductions allocable to excluded foreign income"
    unit = USD
    documentation = "Deductions allowed in figuring AGI that are allocable to excluded foreign earned income and housing amounts: Form 2555 line 44, summed across both spouses on a joint return. These reduce line 45 but not the gross exclusions on line 43. This input only supplies the federal rate worksheet adjustment; other income and deduction inputs retain their existing model definitions."
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/911#d_6",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
    ]
