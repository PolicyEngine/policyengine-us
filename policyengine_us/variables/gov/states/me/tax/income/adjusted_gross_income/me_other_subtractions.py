from policyengine_us.model_api import *


class me_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
    documentation = (
        "Maine other subtraction modifications from federal adjusted gross income "
        "reported on Form 1040ME Schedule 1S, Line 26 (Other subtractions; line 28 in 2022), "
        "entered as a positive amount, excluding subtractions PolicyEngine calculates separately."
    )
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1s_ff.pdf"
