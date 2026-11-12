from policyengine_us.model_api import *


class ia_dependent_claimant_net_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa net income of the person claiming this filer as a dependent"
    unit = USD
    documentation = (
        "For a filer claimed as a dependent on another return, the claiming "
        "person's own net income from all sources under Iowa Code 422.5, "
        "including its addbacks. Zero, so no disqualification, without an "
        "input."
    )
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = (
        # Iowa Code 422.5(3)(a) (2022) and 422.5(2)(a) (2023 onward).
        "https://www.legis.iowa.gov/docs/code/2022/422.5.pdf#page=3",
        # PDF pages 1-2
        "https://www.legis.iowa.gov/docs/code/2024/422.5.pdf#page=1",
    )
