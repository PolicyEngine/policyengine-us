from policyengine_us.model_api import *


class ne_qualifying_contributions_to_eligible_program(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualifying contributions to the establishment or operation of a Nebraska eligible program"
    definition_period = YEAR
    defined_for = StateCode.NE
    reference = (
        "https://revenue.nebraska.gov/about/2023-nebraska-legislative-changes"
    )
