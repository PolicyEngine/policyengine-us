from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_qualified_property_taxes(Variable):
    """Actual pre-credit liability for one parcel and the assessment year.

    Include the whole qualified residential ad valorem component after other
    assessment relief/exemptions. Do not truncate it by this credit's cap or
    prorate it by title share. Exclude personal property, agricultural/pasture/
    timberland, fees, penalties, interest and other nonqualifying charges.
    There is no generic paid-tax fallback or uprating. -1 means missing;
    an explicit 0 is verified zero liability.
    """

    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    default_value = -1
    label = "Arkansas homestead ad valorem liability before the property tax credit"
    reference = (
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2025R%2FPublic%2FACT330.pdf#page=1",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2005%2FPublic%2FACT1268.pdf#page=1",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2023R%2FPublic%2FACT541.pdf#page=2",
    )
