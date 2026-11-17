from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_bill_before_credit(Variable):
    """Optional full bill for the same parcel and assessment year.

    This is the actual bill immediately before this flat credit. It may
    include nonqualifying charges and must be at least the qualified
    liability. There is no uprating or generic paid-tax fallback. Missing
    (-1) or inconsistent bill data do not suppress the core credit.
    """

    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    default_value = -1
    label = "Arkansas parcel's full bill before the homestead property tax credit"
    reference = "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2005%2FPublic%2FACT1268.pdf#page=1"
