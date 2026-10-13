from policyengine_us.model_api import *


class ny_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    documentation = "Other subtractions from federal adjusted gross income reported on Form IT-201, Line 30."
    reference = "https://www.tax.ny.gov/pdf/2024/inc/it201i_2024.pdf#page=10"
