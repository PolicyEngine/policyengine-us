from policyengine_us.model_api import *


class ny_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    documentation = (
        "New York other subtractions from federal adjusted gross income reported on "
        "Form IT-201, line 31 (from Form IT-225, line 18), entered as a positive amount."
    )
    reference = "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=10"
