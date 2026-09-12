from policyengine_us.model_api import *


class ia_ssa_dp_dependent_countable_income(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA dependent person countable income"
    unit = USD
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.51.pdf#page=2"
    )
