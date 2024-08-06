from policyengine_us.model_api import *


class ne_qualifying_contributions_to_eligible_program_with_physical_presence_in_opportunity_zone(
    Variable
):
    value_type = float
    entity = TaxUnit
    label = "Qualifying contributions to an eligible program with a physical presence in an opportunity zone in Nebraska designated pursuant to the federal Tax Cuts and Jobs Act"
    definition_period = YEAR
    defined_for = StateCode.NE
    reference = (
        "https://revenue.nebraska.gov/about/2023-nebraska-legislative-changes"
    )
