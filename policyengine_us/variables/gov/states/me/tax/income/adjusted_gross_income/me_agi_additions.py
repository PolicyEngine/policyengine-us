from policyengine_us.model_api import *


class me_agi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "ME AGI additions"
    unit = USD
    documentation = "Additions to ME AGI over federal AGI."
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = dict(
        title="Schedule 1A, Income Addition Modifications",
        href="https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1a_ff.pdf",
    )
