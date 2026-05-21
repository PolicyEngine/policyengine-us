from policyengine_us.model_api import *


class is_snap_abawd_indian_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Exempt from SNAP ABAWD work requirements due to Indian, Urban Indian, or California Indian status"
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=82",
        "https://www.law.cornell.edu/uscode/text/25/1603",
        "https://www.law.cornell.edu/uscode/text/25/1679",
    )
