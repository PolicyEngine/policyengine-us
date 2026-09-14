from policyengine_us.model_api import *


class ma_ccfa_has_part_time_authorization(Variable):
    value_type = bool
    entity = Person
    label = "Has a Massachusetts CCFA part-time child care authorization"
    documentation = "An actual part-time CCFA authorization for the child. Before- or after-school care alone does not establish part-time authorization."
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=76",
        "https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=46",
    )
