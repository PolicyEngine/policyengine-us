from policyengine_us.model_api import *


class me_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
    documentation = (
        "Maine other addition modifications to federal adjusted gross income "
        "reported on Form 1040ME Schedule 1A, entered as a positive amount."
    )
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1a_ff.pdf"
