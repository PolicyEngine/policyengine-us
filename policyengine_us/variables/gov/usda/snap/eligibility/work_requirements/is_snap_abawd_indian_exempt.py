from policyengine_us.model_api import *


class is_snap_abawd_indian_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Exempt from SNAP ABAWD work requirements due to Indian, Urban Indian, or California Indian status"
    documentation = "Indian or Urban Indian as defined in paragraphs (13) and (28) of section 4 of the Indian Health Care Improvement Act (25 U.S.C. 1603), or California Indian described in section 809(a) of that Act (25 U.S.C. 1679(a)), exempt under 7 U.S.C. 2015(o)(3)(F)-(G) as added by P.L. 119-21. Input variable defaulting to false: survey data do not identify IHCIA status, so this is populated at the data layer (populace) or set explicitly in household simulations."
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=11",
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=12",
        "https://www.law.cornell.edu/uscode/text/25/1603",
        "https://www.law.cornell.edu/uscode/text/25/1679",
    )
