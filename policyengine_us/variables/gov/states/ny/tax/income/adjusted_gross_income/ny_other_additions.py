from policyengine_us.model_api import *


class ny_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    documentation = (
        "New York other additions to federal adjusted gross income reported on "
        "Form IT-201, line 23 (from Form IT-225, line 9), entered as a positive amount."
    )
    # PDF pages 7-8
    reference = "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=7"
