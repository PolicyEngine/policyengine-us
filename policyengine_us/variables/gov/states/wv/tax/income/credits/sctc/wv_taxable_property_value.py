from policyengine_us.model_api import *


class wv_taxable_property_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia taxable property value"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-21/"

    adds = ["assessed_property_value"]
    subtracts = ["wv_homestead_exemption"]
