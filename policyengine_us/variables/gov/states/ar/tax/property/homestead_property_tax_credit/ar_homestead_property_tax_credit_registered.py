from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_registered(Variable):
    """County record/form establishes valid assessment-year registration.

    Include an accepted continuing registration. Check the October 15 deadline
    in the year after assessment and its weekend/USPS-holiday extension;
    required trust/LLC proof, good-standing certificate and no-other-credit
    attestation; and the one-new-claim-per-owner/calendar-year restriction.
    An already attached parcel credit is not automatically an unlawful second
    new claim.
    """

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = "Arkansas accepted the homestead property tax credit registration"
    reference = (
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2023R%2FPublic%2FACT541.pdf#page=1",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2017R%2FPublic%2FACT152.pdf#page=1",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2017R%2FPublic%2FACT49.pdf#page=1",
        "https://sebastiancountyar.gov/Portals/0/Content/Assessor/Downloads/Homestead%20Tax%20Credit%20Form%202026.html",
    )
