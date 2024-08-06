from policyengine_us.model_api import *


class ne_qualifying_contributions_to_eligible_child_care_subsidy_program(
    Variable
):
    value_type = float
    entity = TaxUnit
    label = "Nebraska qualifying contributions to an eligible program with at least one child enrolled in the child care subsidy program established and the child care provider is actively caring and billing for the child"
    definition_period = YEAR
    defined_for = StateCode.NE
    reference = (
        "https://revenue.nebraska.gov/about/2023-nebraska-legislative-changes"
    )
