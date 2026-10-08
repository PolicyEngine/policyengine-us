from policyengine_us.model_api import *


class foreign_housing_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Foreign housing deduction"
    unit = USD
    documentation = "Foreign housing deduction under 26 U.S.C. 911(c)(4): Form 2555 line 50, summed across both spouses on a joint return. This enters the federal stacking worksheet but is not part of the gross exclusions on line 43. This input only supplies the federal rate worksheet adjustment; other income and deduction inputs retain their existing model definitions."
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/911#c_4",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
    ]
