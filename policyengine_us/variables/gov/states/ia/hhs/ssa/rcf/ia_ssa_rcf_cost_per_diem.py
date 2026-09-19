from policyengine_us.model_api import *


class ia_ssa_rcf_cost_per_diem(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA residential care facility actual per diem cost"
    unit = USD
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.52.pdf#page=1"
    )
