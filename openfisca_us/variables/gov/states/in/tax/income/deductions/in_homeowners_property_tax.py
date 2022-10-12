from policyengine_us.model_api import *


class in_homeowners_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN rent"
    unit = USD
    definition_period = YEAR
    documentation = "Property taxes paid on a principal place of residence that was subject to Indiana property tax."
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"
    )
