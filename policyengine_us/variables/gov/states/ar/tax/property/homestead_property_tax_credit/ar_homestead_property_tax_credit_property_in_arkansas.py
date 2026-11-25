from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_property_in_arkansas(Variable):
    """The actual parcel's jurisdiction for this assessment year.

    Current household geography cannot establish or override this fact.
    """

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = "The homestead property tax credit parcel is in Arkansas"
    reference = "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2025R%2FPublic%2FACT330.pdf#page=1"
