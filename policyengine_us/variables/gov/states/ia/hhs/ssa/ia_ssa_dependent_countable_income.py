from policyengine_us.model_api import *


class ia_ssa_dependent_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Countable income of Iowa SSA selected dependent"
    definition_period = MONTH
    unit = USD
    # PDF pages 24-28
    reference = "https://hhs.iowa.gov/media/3987/download?inline=#page=24"
    documentation = "Verified dependent income after 6-B deductions, including the special parent-of-child calculation and only one $20 exclusion per dependent group. The dependent does not receive the recipient's half-earnings exclusion. An entry carries into later months until it is changed."
