from policyengine_us.model_api import *


class me_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "ME AGI subtractions"
    unit = USD
    documentation = "Subtractions from ME AGI over federal AGI."
    definition_period = YEAR
    defined_for = StateCode.ME
    dict(
        title="Schedule 1S, Income Subtraction Modifications",
        href="https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1s_ff.pdf",
    )
