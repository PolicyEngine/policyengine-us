from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_claims_disabled_veteran_exemption(Variable):
    """Actual section 26-3-306 exemption claim relevant to this claim.

    Section 26-3-306(e) prohibits also claiming this credit. Veteran/disability
    status alone does not establish that exemption was claimed.
    """

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = (
        "The Arkansas homestead claimant claims the disabled veteran property exemption"
    )
    reference = "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2001%2FPublic%2FACT1544.pdf#page=1"
