from policyengine_us.model_api import *


class md_hundred_year_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland hundred year subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/hb0186?ys=2022RS"
    )
    defined_for = "md_hundred_year_subtraction_eligible"

    adds = ["md_hundred_year_subtraction_person"]
