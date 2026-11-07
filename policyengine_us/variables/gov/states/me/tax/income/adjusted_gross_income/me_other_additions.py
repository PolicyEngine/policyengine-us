from policyengine_us.model_api import *


class me_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
    documentation = (
        "Maine addition modifications to federal adjusted gross income "
        "reported on Form 1040ME Schedule 1A, Line 11 (Total additions; line 12 in 2022), "
        "entered as a positive amount, excluding additions PolicyEngine calculates separately."
    )
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1a_ff.pdf"
