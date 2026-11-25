from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_facts_available(Variable):
    """Traceable county/parcel evidence establishes the program's facts.

    Verify actual jurisdiction, residence/legal-interest/qualification
    history, registration and duplicate-claim checks, actual disabled-veteran
    exemption claim status and the sole computational recipient. Known false
    qualifications remain available facts; missing evidence must not be
    reported as legal ineligibility.
    """

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = "Verified Arkansas homestead parcel and claim facts are available"
    reference = (
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2023R%2FPublic%2FACT541.pdf#page=1",
        "https://sebastiancountyar.gov/Portals/0/Content/Assessor/Downloads/Homestead%20Tax%20Credit%20Form%202026.html",
    )
