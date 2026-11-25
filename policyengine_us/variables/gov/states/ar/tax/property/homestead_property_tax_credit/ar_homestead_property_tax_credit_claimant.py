from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_claimant(Variable):
    """Attribute one complete parcel record to exactly one TaxUnit.

    This is computational attribution, not sole legal ownership or a filing
    condition. Co-owners/spouses do not multiply or automatically prorate the
    parcel credit. Other TaxUnits must not receive another copy of the same
    parcel's complete liability record.
    """

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = (
        "This tax unit receives the Arkansas parcel's single homestead credit record"
    )
    reference = (
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2005%2FPublic%2FACT1268.pdf#page=2",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2017R%2FPublic%2FACT49.pdf#page=1",
    )
