from policyengine_us.model_api import *


class deductible_mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "Deductible mortgage interest"
    documentation = "Under the interest deduction, the US caps the mortgage value to which interest is applied which based on the year of purchase not tax year."
    unit = USD
    definition_period = YEAR

    # This is a placeholder variable until we can implement the full mortgage interest deduction logic
