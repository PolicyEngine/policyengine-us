
from policyengine_us.model_api import *


class per_capita_chip(Variable):
    value_type = float
    entity = Person
    label = "Average CHIP payment"
    unit = USD
    documentation = "Per-capita CHIP payment for this person's State."
    definition_period = YEAR
    reference = "https://www.macpac.gov/publication/chip-spending-by-state/"

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        # Get total spending for Medicaid expansion CHIP
        spending = parameters(period).gov.hhs.chip.spending.medicaid_expansion_chip.total[state]
        # Get total enrollment
        enrollment = parameters(period).gov.hhs.chip.enrollment.total[state]
        # Avoid division by zero
        return np.divide(
            spending, 
            enrollment, 
            out=np.zeros_like(spending), 
            where=enrollment > 0
        )