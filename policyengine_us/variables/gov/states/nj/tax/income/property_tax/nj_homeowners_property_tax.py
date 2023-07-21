from policyengine_us.model_api import *


class nj_homeowners_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "NJ Homeowner's Property Taxes"
    unit = USD
    definition_period = YEAR
    documentation = "Property taxes or rent paid on a principal place of residence that was subject to New Jersey property tax."
    reference = "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=26"
    defined_for = StateCode.NJ

    # By default, use real estate taxes.
    adds = ["real_estate_taxes"]
