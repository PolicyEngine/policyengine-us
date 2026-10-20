from policyengine_us.model_api import *


class nm_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
    documentation = (
        "New Mexico other additions to federal adjusted gross income reported on "
        "Form PIT-ADJ, entered as a positive amount, excluding additions PolicyEngine "
        "calculates separately."
    )
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/97f27f33-5e23-4a25-ad68-0980a22b802d/PITbook2024.pdf#page=15"
